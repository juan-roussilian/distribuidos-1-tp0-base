package common

import (
	"net"
)

const MaxBatchMessageSize = 8000

type Messenger struct {
	serializer Serializer
}

func NewMessenger() *Messenger {
	messenger := &Messenger{
		serializer: Serializer{},
	}
	return messenger
}

// SendBet sends a bet to the server
func (m *Messenger) SendBets(connection net.Conn, bets []Bet, clientID uint16) error {

	betsBytes := m.serializer.SerializeBets(bets, clientID)

	if len(betsBytes) < MaxBatchMessageSize {
		padding := make([]byte, MaxBatchMessageSize-len(betsBytes))
		betsBytes = append(betsBytes, padding...)
	}

	if err := writeAll(connection, betsBytes); err != nil {
		return err
	}
	return nil
}

func (m *Messenger) ReceiveResult(connection net.Conn, clientID uint16) (int16, error) {
	buffer, err := readAll(connection, 2)

	if err != nil {
		return -1, err
	}
	responseOpcode := m.serializer.deserializeOpcode(buffer)
	return int16(responseOpcode), nil
}

// WriteAll ensures that all bytes are written to the connection
func writeAll(conn net.Conn, data []byte) error {
	totalSent := 0
	for totalSent < len(data) {
		sent, err := conn.Write(data[totalSent:])
		if err != nil {
			return err
		}
		totalSent += sent
	}
	return nil
}

// ReadAll ensures that exactly 'size' bytes are read from the connection
func readAll(conn net.Conn, size int) ([]byte, error) {
	buffer := make([]byte, size)
	totalRead := 0
	for totalRead < size {
		n, err := conn.Read(buffer[totalRead:])
		if err != nil {
			return nil, err
		}
		totalRead += n
	}
	return buffer, nil
}
