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
func (m *Messenger) SendBets(connection net.Conn, bets []Bet, clientID uint16) error {

	betsBytes, serializer_err := m.serializer.SerializeBets(bets, clientID)

	if serializer_err != nil {
		return serializer_err
	}
	if len(betsBytes) > MaxBatchMessageSize {
		return errors.New("batch size is too large and cannot exceed 8000 bytes")
	}

	if send_err := writeAll(connection, betsBytes); send_err != nil {
		return send_err
	}
	return nil
}

func (m *Messenger) ReceiveResult(connection net.Conn, clientID uint16) (int16, error) {
	buffer, err := readAll(connection, 2)

	if err != nil {
		return -1, err
	}
	responseOpcode := m.serializer.deserializeUInt16(buffer)
	return int16(responseOpcode), nil
}

func (m *Messenger) SendEndOfBets(connection net.Conn, clientID uint16) error {
	endOfBetsBytes := m.serializer.SerializeOpcodeAndClientID(EndOfBatchOpcode, clientID)
	if send_err := writeAll(connection, endOfBetsBytes); send_err != nil {
		return send_err
	}
	return nil
}

func (m *Messenger) AskForWinners(connection net.Conn, clientID uint16) error {
	askWinnersBytes := m.serializer.SerializeOpcodeAndClientID(AskWinnersOpcode, clientID)
	if send_err := writeAll(connection, askWinnersBytes); send_err != nil {
		return send_err
	}
	return nil
}

func (m *Messenger) ReceiveWinners(connection net.Conn) []uint16 {
	numWinnersBytes, read_err := readAll(connection, 2)
	if read_err != nil {
		return nil
	}

	numWinners := m.serializer.deserializeUInt16(numWinnersBytes)

	winners := make([]uint16, numWinners)
	for i := uint16(0); i < numWinners; i++ {
		winnerNumberBytes, read_err := readAll(connection, 2)
		if read_err != nil {
			return nil
		}

		winners[i] = m.serializer.deserializeUInt16(winnerNumberBytes)
	}
	return winners
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
