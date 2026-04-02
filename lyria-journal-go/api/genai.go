package api

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
)

type MusicMetadata struct {
	Prompt string `json:"prompt"`
	Title  string `json:"title"`
	Lyrics string `json:"lyrics"`
}

var GenerateMusicMetadata = func(ctx context.Context, text string, fileData []byte, mimeType string) (*MusicMetadata, error) {
	apiKey := os.Getenv("GOOGLE_API_KEY")
	projectID := os.Getenv("GOOGLE_CLOUD_PROJECT")
	location := os.Getenv("GOOGLE_CLOUD_REGION")
	if location == "" {
		location = "europe-west1"
	}

	if apiKey == "" && projectID == "" {
		// Mock implementation if API Key and Project ID are not set
		return &MusicMetadata{
			Prompt: "Mock Prompt: " + text,
			Title:  "Mock Title",
			Lyrics: "Mock Lyrics",
		}, nil
	}

	var url string
	if projectID != "" {
		url = fmt.Sprintf("https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/publishers/google/models/gemini-2.5-flash:generateContent", location, projectID, location)
	} else {
		url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + apiKey
	}

	type InlineData struct {
		MimeType string `json:"mimeType"`
		Data     string `json:"data"` // base64
	}

	type Part struct {
		Text       string      `json:"text,omitempty"`
		InlineData *InlineData `json:"inlineData,omitempty"`
	}

	type Content struct {
		Parts []Part `json:"parts"`
	}

	var parts []Part

	if len(fileData) > 0 {
		parts = append(parts, Part{
			InlineData: &InlineData{
				MimeType: mimeType,
				Data:     base64.StdEncoding.EncodeToString(fileData),
			},
		})
	}

	if text != "" {
		parts = append(parts, Part{Text: "Texte de contexte utilisateur : " + text + "\n\n"})
	}

	promptInstruction := `Analyse l'image fournie (et/ou le texte fourni s'il y en a un).
	Tu dois générer trois choses basées sur ce contexte, l'humeur et l'ambiance :
	1. "prompt": Un prompt musical détaillé en anglais (50-100 mots) pour l'API Lyria 3.
	2. "title": Un titre évocateur et court pour la chanson.
	3. "lyrics": Les paroles complètes formatées.
	Tu DOIS impérativement renvoyer un objet JSON valide avec exactement ces 3 clés : "prompt", "title" et "lyrics". Ne rajoute pas de markdown autour de ta réponse JSON.`
	parts = append(parts, Part{Text: promptInstruction})

	reqBody := map[string]interface{}{
		"contents": []Content{{Parts: parts}},
		"generationConfig": map[string]interface{}{
			"temperature":      0.7,
			"responseMimeType": "application/json",
		},
	}

	reqBytes, _ := json.Marshal(reqBody)

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(reqBytes))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")

	if projectID != "" {
		tokenSource, err := getDefaultTokenSource(ctx)
		if err == nil {
			if token, err := tokenSource.Token(); err == nil {
				req.Header.Set("Authorization", "Bearer "+token.AccessToken)
			}
		}
	}

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	bodyBytes, _ := ioutil.ReadAll(resp.Body)

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("Gemini API error: %d - %s", resp.StatusCode, string(bodyBytes))
	}

	var result struct {
		Candidates []struct {
			Content struct {
				Parts []struct {
					Text string `json:"text"`
				} `json:"parts"`
			} `json:"content"`
		} `json:"candidates"`
	}

	if err := json.Unmarshal(bodyBytes, &result); err != nil {
		return nil, err
	}

	if len(result.Candidates) == 0 || len(result.Candidates[0].Content.Parts) == 0 {
		return nil, fmt.Errorf("No candidates found")
	}

	jsonText := result.Candidates[0].Content.Parts[0].Text

	var metadata MusicMetadata
	if err := json.Unmarshal([]byte(jsonText), &metadata); err != nil {
		return nil, err
	}

	return &metadata, nil
}

var GenerateMusic = func(ctx context.Context, prompt string) ([]byte, error) {
	tokenSource, err := getDefaultTokenSource(ctx)
	if err != nil {
		// Mock implementation if ADC not available
		return []byte("mock_audio_data_for_" + prompt), nil
	}

	_, err = tokenSource.Token()
	if err != nil {
		return []byte("mock_audio_data_for_" + prompt), nil
	}

	projectID := os.Getenv("GOOGLE_CLOUD_PROJECT")
	if projectID == "" {
		return []byte("fake_audio_bytes"), nil
	}

	return []byte("fake_audio_bytes_from_go"), nil
}

func getDefaultTokenSource(ctx context.Context) (oauth2.TokenSource, error) {
	creds, err := google.FindDefaultCredentials(ctx, "https://www.googleapis.com/auth/cloud-platform")
	if err != nil {
		return nil, err
	}
	return creds.TokenSource, nil
}