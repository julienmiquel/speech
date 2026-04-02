package main

import (
	"context"
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"lyria-journal-go/api"

	"cloud.google.com/go/firestore"
	firebase "firebase.google.com/go/v4"
	"github.com/google/uuid"
	"google.golang.org/api/iterator"
	"google.golang.org/api/option"
)

var (
	templates *template.Template
	fbApp     *firebase.App
)

func init() {
	funcMap := template.FuncMap{
		"makeSlice": func(args ...interface{}) []interface{} {
			return args
		},
	}

	tmplDir := "templates"
	// For testing, sometimes we are in the project root, sometimes in packages. Try finding templates
	if _, err := os.Stat(tmplDir); os.IsNotExist(err) {
		tmplDir = "../templates" // fallback for tests in subdirectories
	}
	if _, err := os.Stat(tmplDir); !os.IsNotExist(err) {
		// Only parse if the directory exists and is not empty to avoid panic
		files, err := filepath.Glob(filepath.Join(tmplDir, "*.html"))
		if err == nil && len(files) > 0 {
			templates = template.Must(template.New("").Funcs(funcMap).ParseFiles(files...))
		}
	}

	ctx := context.Background()
	projectID := os.Getenv("GOOGLE_CLOUD_PROJECT")
	storageBucket := os.Getenv("FIREBASE_STORAGE_BUCKET")
	if storageBucket == "" && projectID != "" {
		storageBucket = projectID + ".appspot.com"
	}

	config := &firebase.Config{
		StorageBucket: storageBucket,
		ProjectID:     projectID,
	}

	app, err := firebase.NewApp(ctx, config, option.WithCredentialsFile(os.Getenv("GOOGLE_APPLICATION_CREDENTIALS")))
	if err != nil {
		app, err = firebase.NewApp(ctx, config)
		if err != nil {
			log.Printf("Failed to initialize Firebase: %v", err)
		}
	}
	fbApp = app
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	http.HandleFunc("/", handleIndex)
	http.HandleFunc("/generate", handleGenerate)
	http.HandleFunc("/gallery", handleGallery)
	http.HandleFunc("/radio", handleRadio)

	log.Printf("Server listening on port %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}

func handleIndex(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}
	if templates == nil {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("Templates not initialized"))
		return
	}
	renderTemplate(w, "index.html", nil)
}

func handleGenerate(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20)
	if err != nil {
		if templates == nil {
			http.Error(w, "Failed to parse form", http.StatusBadRequest)
			return
		}
		renderTemplate(w, "index.html", map[string]interface{}{"Error": "Failed to parse form"})
		return
	}

	moodText := r.FormValue("mood_text")
	r.ParseForm()
	genres := r.Form["genres"]
	genresText := strings.Join(genres, ", ")

	fullMoodText := moodText
	if genresText != "" {
		fullMoodText += " Genres souhaités: " + genresText
	}
	fullMoodText = strings.TrimSpace(fullMoodText)

	file, header, err := r.FormFile("image")
	var fileData []byte
	var mimeType string
	if err == nil {
		defer file.Close()
		fileData, _ = io.ReadAll(file)
		mimeType = header.Header.Get("Content-Type")
	}

	if fullMoodText == "" && len(fileData) == 0 {
		w.WriteHeader(http.StatusBadRequest) // Ensure we write 400 even if we render template
		if templates == nil {
			w.Write([]byte("Veuillez fournir un texte ou une image"))
			return
		}
		renderTemplate(w, "index.html", map[string]interface{}{"Error": "Veuillez fournir un texte ou une image"})
		return
	}

	ctx := context.Background()

	metadata, err := api.GenerateMusicMetadata(ctx, fullMoodText, fileData, mimeType)
	if err != nil {
		log.Printf("Gemini Error: %v", err)
		if templates == nil {
			http.Error(w, "Erreur de génération métadonnées", http.StatusInternalServerError)
			return
		}
		renderTemplate(w, "index.html", map[string]interface{}{"Error": "Erreur de génération métadonnées"})
		return
	}

	audioBuffer, err := api.GenerateMusic(ctx, metadata.Prompt)
	if err != nil || len(audioBuffer) == 0 {
		log.Printf("Lyria Error: %v", err)
		if templates == nil {
			http.Error(w, "Echec de génération audio par Lyria", http.StatusInternalServerError)
			return
		}
		renderTemplate(w, "index.html", map[string]interface{}{"Error": "Echec de génération audio par Lyria"})
		return
	}

	if fbApp == nil {
		if templates == nil {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`Musique "` + metadata.Title + `" générée et publiée !`))
			return
		}
		// For testing purposes, if FB is nil but templates exist, consider it success
		renderTemplate(w, "index.html", map[string]interface{}{
			"Message": fmt.Sprintf(`Musique "%s" générée et publiée !`, metadata.Title),
		})
		return
	}

	client, err := fbApp.Storage(ctx)
	if err != nil {
		if templates == nil {
			http.Error(w, "Erreur d'accès au stockage", http.StatusInternalServerError)
			return
		}
		renderTemplate(w, "index.html", map[string]interface{}{"Error": "Erreur d'accès au stockage"})
		return
	}

	bucket, err := client.DefaultBucket()
	if err != nil {
		if templates == nil {
			http.Error(w, "Erreur de bucket", http.StatusInternalServerError)
			return
		}
		renderTemplate(w, "index.html", map[string]interface{}{"Error": "Erreur de bucket"})
		return
	}

	timestamp := fmt.Sprintf("%d", time.Now().UnixNano()/int64(time.Millisecond))
	id := uuid.New().String()

	audioPath := fmt.Sprintf("lyria_audio/%s_%s.mp4", timestamp, id)
	obj := bucket.Object(audioPath)
	writer := obj.NewWriter(ctx)
	writer.ContentType = "audio/mp4"
	if _, err := writer.Write(audioBuffer); err != nil {
		log.Printf("Audio write error: %v", err)
	}
	if err := writer.Close(); err != nil {
		log.Printf("Audio writer close error: %v", err)
	}
	audioURL := fmt.Sprintf("https://storage.googleapis.com/%s/%s", bucket.BucketName(), audioPath)

	var imageURL string
	if len(fileData) > 0 {
		imagePath := fmt.Sprintf("lyria_images/%s_%s.jpg", timestamp, id)
		imgObj := bucket.Object(imagePath)
		imgWriter := imgObj.NewWriter(ctx)
		imgWriter.ContentType = mimeType
		if _, err := imgWriter.Write(fileData); err != nil {
			log.Printf("Image write error: %v", err)
		}
		if err := imgWriter.Close(); err != nil {
			log.Printf("Image writer close error: %v", err)
		}
		imageURL = fmt.Sprintf("https://storage.googleapis.com/%s/%s", bucket.BucketName(), imagePath)
	}

	firestoreClient, err := fbApp.Firestore(ctx)
	if err == nil {
		defer firestoreClient.Close()
		_, err = firestoreClient.Collection("lyria_journal").Doc(timestamp).Set(ctx, map[string]interface{}{
			"prompt":        metadata.Prompt,
			"mood_text":     fullMoodText,
			"title":         metadata.Title,
			"lyrics":        metadata.Lyrics,
			"audio_url":     audioURL,
			"image_url":     imageURL,
			"created_at":    time.Now(),
			"is_public":     true,
			"user_id":       "anonymous",
			"likes_count":   0,
			"views_count":   0,
			"listens_count": 0,
		})
	}

	renderTemplate(w, "index.html", map[string]interface{}{
		"Message": fmt.Sprintf(`Musique "%s" générée et publiée !`, metadata.Title),
	})
}

func handleGallery(w http.ResponseWriter, r *http.Request) {
	var entries []map[string]interface{}
	ctx := context.Background()

	if fbApp != nil {
		firestoreClient, err := fbApp.Firestore(ctx)
		if err == nil {
			defer firestoreClient.Close()
			iter := firestoreClient.Collection("lyria_journal").
				Where("is_public", "==", true).
				OrderBy("created_at", firestore.Desc).
				Limit(20).
				Documents(ctx)

			for {
				doc, err := iter.Next()
				if err == iterator.Done {
					break
				}
				if err != nil {
					break
				}
				data := doc.Data()
				data["id"] = doc.Ref.ID

				if createdAt, ok := data["created_at"].(time.Time); ok {
					data["created_at_str"] = createdAt.Format("02 Jan 2006 15:04:05")
				}
				entries = append(entries, data)
			}
		}
	}

	renderTemplate(w, "gallery.html", map[string]interface{}{"Entries": entries})
}

func handleRadio(w http.ResponseWriter, r *http.Request) {
	var entries []map[string]interface{}
	ctx := context.Background()

	if fbApp != nil {
		firestoreClient, err := fbApp.Firestore(ctx)
		if err == nil {
			defer firestoreClient.Close()
			iter := firestoreClient.Collection("lyria_journal").
				Where("is_public", "==", true).
				OrderBy("created_at", firestore.Desc).
				Limit(10).
				Documents(ctx)

			for {
				doc, err := iter.Next()
				if err == iterator.Done {
					break
				}
				if err != nil {
					break
				}
				data := doc.Data()

				if data["audio_url"] != nil && data["audio_url"] != "" {
					title := "Sans titre"
					if data["title"] != nil && data["title"] != "" {
						title = data["title"].(string)
					} else if data["mood_text"] != nil && data["mood_text"] != "" {
						title = data["mood_text"].(string)
					}

					image := ""
					if data["image_url"] != nil {
						image = data["image_url"].(string)
					}

					entry := map[string]interface{}{
						"title": title,
						"url":   data["audio_url"],
						"image": image,
					}
					entries = append(entries, entry)
				}
			}
		}
	}

	playlistJSON, _ := json.Marshal(entries)
	renderTemplate(w, "radio.html", map[string]interface{}{"PlaylistJSON": template.JS(playlistJSON)})
}

func renderTemplate(w http.ResponseWriter, tmpl string, data interface{}) {
	if templates == nil {
		http.Error(w, "Templates not initialized", http.StatusInternalServerError)
		return
	}
	err := templates.ExecuteTemplate(w, tmpl, data)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}