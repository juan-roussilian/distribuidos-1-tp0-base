package common

import (
	"encoding/binary"
	"errors"
)

const SendBetBatchOpcode = 1
const BetPayloadSize = 144

type Serializer struct{}

func (s *Serializer) int16ToBytes(n uint16) []byte {
	b := make([]byte, 2)
	binary.BigEndian.PutUint16(b, uint16(n))
	return b
}

func (s *Serializer) int32ToBytes(n uint32) []byte {
	b := make([]byte, 4)
	binary.BigEndian.PutUint32(b, uint32(n))
	return b
}

func (s *Serializer) deserializeOpcode(data []byte) uint16 {
	return binary.BigEndian.Uint16(data)
}

func (s *Serializer) SerializeBets(bets []Bet, clientID uint16) ([]byte, error) {

	// Convert "header" values to bytes and append at first 6 message bytes
	// (2 bytes for opcode, 2 bytes for clientID, 2 bytes for number of bets)
	opcodeBytes := s.int16ToBytes(SendBetBatchOpcode)
	data := append(opcodeBytes, s.int16ToBytes(clientID)...)
	data = append(data, s.int16ToBytes(uint16(len(bets)))...)

	for _, bet := range bets {

		betNumberBytes := s.int16ToBytes(bet.Number)
		documentBytes := s.int32ToBytes(bet.Document)

		// Convert dynamic-length strings to bytes and calculate its length
		firstNameBytes := []byte(bet.FirstName)
		firstNameLenBytes := s.int16ToBytes(uint16(len(firstNameBytes)))

		lastNameBytes := []byte(bet.LastName)
		lastNameLenBytes := s.int16ToBytes(uint16(len(lastNameBytes)))

		// Assume BirthDate is always a 10 byte string
		birthDateBytes := []byte(bet.BirthDate)

		// Combine all byte slices into one and add padding if necesary
		bet_bytes := append(documentBytes, betNumberBytes...)
		bet_bytes = append(bet_bytes, birthDateBytes...)
		bet_bytes = append(bet_bytes, firstNameLenBytes...)
		bet_bytes = append(bet_bytes, firstNameBytes...)
		bet_bytes = append(bet_bytes, lastNameLenBytes...)
		bet_bytes = append(bet_bytes, lastNameBytes...)

		if len(bet_bytes) < BetPayloadSize {
			padding := make([]byte, BetPayloadSize-len(bet_bytes))
			bet_bytes = append(bet_bytes, padding...)
		} else if len(bet_bytes) > BetPayloadSize {
			return nil, errors.New("bet fields size is too large")
		}
		data = append(data, bet_bytes...)
	}

	return data, nil
}
