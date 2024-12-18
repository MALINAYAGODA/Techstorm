package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"

	"github.com/labstack/echo/v4"

	"service-portal/internal/generated/rpc"
	"service-portal/internal/renderer"
	serperClient "service-portal/internal/serper_client"
	"service-portal/internal/server"
)

func main() {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	log := slog.New(slog.NewJSONHandler(os.Stdout, nil))

	defer func() {
		if err := recover(); err != nil {
			log.Error(fmt.Sprint(err))
			os.Exit(1)
		}
		os.Exit(0)
	}()

	serpClient := serperClient.New(os.Getenv("SERPER_API_KEY"))
	rendererService := renderer.NewService(ctx)

	rpcServer := server.New(log, serpClient, rendererService)

	echoInstance := echo.New()
	rpc.RegisterHandlers(echoInstance, rpc.NewStrictHandler(rpcServer, nil))

	if err := echoInstance.Start(":" + envString("APP_PORT", "8080")); err != nil {
		log.Error(fmt.Sprintf("Router failed: %s", err.Error()))
	}
}

func envString(key, defaultValue string) string {
	if val, ok := os.LookupEnv(key); ok {
		return val
	}
	return defaultValue
}
