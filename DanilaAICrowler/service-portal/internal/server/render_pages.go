package server

import (
	"context"

	"service-portal/internal/generated/rpc"
)

func (s *Server) RenderPages(ctx context.Context, request rpc.RenderPagesRequestObject) (rpc.RenderPagesResponseObject, error) {
	if len(request.Body.Urls) == 0 {
		return rpc.RenderPages200JSONResponse{}, nil
	}

	rendered := s.rendererService.Render(request.Body.Urls)
	rpcResults := make([]rpc.RenderResult, 0, len(rendered))
	for _, v := range rendered {
		if v.Error != nil {
			s.log.ErrorContext(ctx, "error rendering page: %s", v.Error.Error())
			continue
		}

		rpcResults = append(rpcResults, rpc.RenderResult{
			PageText:     v.PageText,
			RenderedHtml: v.PageHtml,
			Url:          v.URL,
		})
	}

	return rpc.RenderPages200JSONResponse{
		Status: 200,
		Result: struct {
			CompleteTasks []rpc.RenderResult `json:"completeTasks"`
		}(struct{ CompleteTasks []rpc.RenderResult }{
			CompleteTasks: rpcResults,
		}),
	}, nil
}
