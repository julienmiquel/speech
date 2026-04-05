package main

import (
	"bytes"
	"context"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"lyria-journal-go/api"
)

func TestHandleIndex(t *testing.T) {
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(handleIndex)
	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}
}

func TestHandleGenerateWithInput(t *testing.T) {
	// Mock the generation functions
	originalGenerateMusicMetadata := api.GenerateMusicMetadata
	originalGenerateMusic := api.GenerateMusic

	api.GenerateMusicMetadata = func(ctx context.Context, text string, fileData []byte, mimeType string) (*api.MusicMetadata, error) {
		return &api.MusicMetadata{
			Prompt: "1980s synth-pop",
			Title:  "Test Song",
			Lyrics: "Test Lyrics",
		}, nil
	}

	api.GenerateMusic = func(ctx context.Context, prompt string) ([]byte, error) {
		return []byte("fake_audio_bytes"), nil
	}

	defer func() {
		api.GenerateMusicMetadata = originalGenerateMusicMetadata
		api.GenerateMusic = originalGenerateMusic
	}()

	body := new(bytes.Buffer)
	writer := multipart.NewWriter(body)
	_ = writer.WriteField("mood_text", "Happy day")
	writer.Close()

	req, err := http.NewRequest("POST", "/generate", body)
	if err != nil {
		t.Fatal(err)
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(handleGenerate)
	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}

	// Because we don't have a fully initialized Firebase mock, it will fail at Firebase init in the handler
	// But we expect it to try to render the error or success template.
	// Since templates aren't loaded in test dir context without setup, it will 500 with "Templates not initialized"
	// Since templates aren't loaded and Firebase is mocked properly now in handler for missing templates
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}
}

func TestHandleGenerateWithoutInput(t *testing.T) {
	body := new(bytes.Buffer)
	writer := multipart.NewWriter(body)
	writer.Close()

	req, err := http.NewRequest("POST", "/generate", body)
	if err != nil {
		t.Fatal(err)
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(handleGenerate)
	handler.ServeHTTP(rr, req)

	// Since we mock nothing, but there's no input, it should fail early with "Veuillez fournir un texte ou une image"
	if rr.Code != http.StatusBadRequest {
		t.Errorf("handler returned wrong status code: got %v want %v", rr.Code, http.StatusBadRequest)
	}
	if !strings.Contains(rr.Body.String(), "Veuillez fournir un texte ou une image") {
		t.Errorf("Expected 'Veuillez fournir un texte ou une image' in body, got: %v", rr.Body.String())
	}
}