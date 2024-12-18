package renderer

import (
	"fmt"
	"strings"
	"sync"

	"github.com/PuerkitoBio/goquery"
	"github.com/go-rod/rod"
)

func (s *Service) Render(urls []string) []RenderResult {
	browser := s.browserPool.Get()
	defer s.browserPool.Put(browser)

	var wg sync.WaitGroup
	var results = make([]RenderResult, len(urls))

	for i, u := range urls {
		wg.Add(1)

		go func() {
			defer wg.Done()

			results[i].URL = u
			err := rod.Try(func() {
				page := browser.MustPage(u)
				defer page.MustClose()

				page.MustWaitLoad()
				results[i].PageHtml = mustCleanHTML(page.MustHTML())
				results[i].PageText = page.MustElement("html").MustText()
			})
			if err != nil {
				results[i].Error = err
			}
		}()

	}

	wg.Wait()
	return results
}

func mustCleanHTML(html string) string {
	doc, err := goquery.NewDocumentFromReader(strings.NewReader(html))
	if err != nil {
		panic(err)
	}

	doc.Find("script").Remove()
	doc.Find("style").Remove()
	doc.Find("*").RemoveAttr("style").RemoveAttr("class")

	result, err := doc.Html()
	if err != nil {
		panic(fmt.Sprintf("unable to render back html: %w", err))
	}

	return result
}
