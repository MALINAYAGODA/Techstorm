package renderer

import (
	"context"

	"github.com/go-rod/rod"
	"github.com/go-rod/rod/lib/launcher"

	"service-portal/internal/renderer/utils"
)

type Service struct {
	browserPool utils.Pool[rod.Browser]
}

func NewService(ctx context.Context) *Service {
	var browsers []*rod.Browser
	for range 10 {
		browsers = append(browsers, setupBrowser())
	}

	go func() {
		<-ctx.Done()
		for _, b := range browsers {
			b.MustClose()
		}
	}()

	return &Service{utils.NewPool(browsers)}
}

func setupBrowser() *rod.Browser {
	l := launcher.New().
		Headless(true)

	browserUrl := l.MustLaunch()

	browser := rod.New().
		ControlURL(browserUrl).
		MustConnect()

	return browser
}
