package serper_client

import (
	"context"
	"fmt"

	"github.com/carlmjohnson/requests"
)

type Client struct {
	apiKey string
}

func New(apiKey string) *Client {
	return &Client{apiKey: apiKey}
}

func (c *Client) GoogleSearch(ctx context.Context, query string) (*SearchResult, error) {
	var result SearchResult

	err := requests.
		URL("https://google.serper.dev/search").
		Post().
		BodyJSON(map[string]string{
			"q": query,
		}).
		Headers(map[string][]string{
			"X-API-KEY":    {c.apiKey},
			"Content-Type": {"application/json"},
		}).
		ToJSON(&result).
		Fetch(ctx)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}

	return &result, nil
}
