package server

import (
	"context"

	"service-portal/internal/generated/rpc"
	serperClient "service-portal/internal/serper_client"
)

func (s *Server) PerformSearch(ctx context.Context, request rpc.PerformSearchRequestObject) (rpc.PerformSearchResponseObject, error) {
	query := request.Body.Query

	if len(query) < 3 {
		return rpc.PerformSearch400JSONResponse{BadRequestJSONResponse: rpc.BadRequestJSONResponse{
			Code:    400,
			Message: "query is empty or less than 3 symbols",
		}}, nil
	}

	result, err := s.serperClient.GoogleSearch(ctx, query)
	if err != nil {
		s.log.ErrorContext(ctx, "failed to perform search", "error", err)
		return rpc.PerformSearch500JSONResponse{rpc.InternalErrorJSONResponse{
			Code: 500,
			Data: map[string]any{
				"error": err.Error(),
			},
			Message: "failed to perform search",
		}}, nil
	}

	return rpc.PerformSearch200JSONResponse{
		Status: 200,
		Result: struct {
			Snippets []rpc.SearchSnippet `json:"snippets"`
		}{Snippets: convertSnippets(result.Organic)},
	}, nil
}

func convertSnippets(snippets []serperClient.SearchSnippet) []rpc.SearchSnippet {
	result := make([]rpc.SearchSnippet, len(snippets))
	for i, s := range snippets {
		result[i] = rpc.SearchSnippet{
			Attributes:  s.Attributes,
			Currency:    s.Currency,
			Description: s.Description,
			ImageUrl:    s.ImageUrl,
			Link:        s.Link,
			Position:    s.Position,
			Price:       s.Price,
			Rating:      s.Rating,
			RatingCount: s.RatingCount,
			Title:       s.Title,
		}
	}
	return result
}
