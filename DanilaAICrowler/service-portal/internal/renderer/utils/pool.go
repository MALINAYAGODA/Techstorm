package utils

type Pool[T any] chan *T

func NewPool[T any](elems []*T) Pool[T] {
	p := make(Pool[T], len(elems))
	for _, elem := range elems {
		p <- elem
	}
	return p
}

// Get tries to take item from pool or block if pool is empty.
func (pool Pool[T]) Get() *T {
	return <-pool
}

func (pool Pool[T]) GetNonBlocking() (*T, bool) {
	select {
	case elem := <-pool:
		return elem, true
	default:
		return nil, false
	}
}

func (pool Pool[T]) Put(elem *T) {
	pool <- elem
}
