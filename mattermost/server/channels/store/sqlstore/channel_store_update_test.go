package sqlstore

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestValidateChannelUpdateCount(t *testing.T) {
	t.Run("missing channel is a not found error", func(t *testing.T) {
		err := validateChannelUpdateCount(0, "channel-1")
		require.EqualError(t, err, "resource \"Channel\" not found, id: channel-1")
	})

	t.Run("one updated row succeeds", func(t *testing.T) {
		require.NoError(t, validateChannelUpdateCount(1, "channel-1"))
	})

	t.Run("unexpected multiple rows remains an error", func(t *testing.T) {
		err := validateChannelUpdateCount(2, "channel-1")
		require.EqualError(t, err, "the expected number of channels to be updated is <=1 but was 2")
	})
}
