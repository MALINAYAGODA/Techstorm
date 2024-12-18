package serper_client

type SearchResult struct {
	Organic []SearchSnippet `json:"organic,omitempty"`
}

type SearchSnippet struct {
	Title       string             `json:"title"`
	Description string             `json:"snippet"`
	Link        string             `json:"link"`
	Position    int                `json:"position"`
	ImageUrl    *string            `json:"imageUrl"`
	Price       *float32           `json:"price"`
	Currency    *string            `json:"currency"`
	Rating      *float32           `json:"rating"`
	RatingCount *int               `json:"ratingCount"`
	Attributes  *map[string]string `json:"attributes"`
}
