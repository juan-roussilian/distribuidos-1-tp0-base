package common

import (
	"errors"
	"net"
)

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
func (m *Messenger) SendBet(connection net.Conn, bet Bet, clientID uint16) error {

	betBytes := m.serializer.SerializeBet(bet, clientID)

	// Ensure betBytes has a length of 150 bytes by padding it with 0s in case its shorter
	if len(betBytes) > 150 {
		return errors.New("bet fields are too long")
	} else if len(betBytes) < 150 {
		padding := make([]byte, 150-len(betBytes))
		betBytes = append(betBytes, padding...)
	}

	if err := writeAll(connection, betBytes); err != nil {
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
