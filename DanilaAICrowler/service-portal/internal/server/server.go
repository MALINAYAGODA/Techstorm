package server

import (
	"log/slog"

	"service-portal/internal/generated/rpc"
	"service-portal/internal/renderer"
	serperClient "service-portal/internal/serper_client"
)

type Server struct {
	log             *slog.Logger
	serperClient    *serperClient.Client
	rendererService *renderer.Service
}

func New(log *slog.Logger, serperClient *serperClient.Client, rendererService *renderer.Service) rpc.StrictServerInterface {
	return &Server{
		log:             log,
		serperClient:    serperClient,
		rendererService: rendererService,
	}
}
