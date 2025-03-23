package common

import (
	"encoding/binary"
)

const SendBetOpcode = 0

type Serializer struct{}

// Convert an int16 to a 2-byte slice
func (s *Serializer) int16ToBytes(n uint16) []byte {
	b := make([]byte, 2)
	binary.BigEndian.PutUint16(b, uint16(n))
	return b
}

// Convert an int32 to a 4-byte slice
func (s *Serializer) int32ToBytes(n uint32) []byte {
	b := make([]byte, 4)
	binary.BigEndian.PutUint32(b, uint32(n))
	return b
}

func (s *Serializer) deserializeOpcode(data []byte) uint16 {
	return binary.BigEndian.Uint16(data)
}

// Serialize a Bet object into a byte slice
func (s *Serializer) SerializeBet(bet Bet, clientID uint16) []byte {

	// Convert integers values  to bytes
	opcodeBytes := s.int16ToBytes(SendBetOpcode)
	betNumberBytes := s.int16ToBytes(bet.Number)
	documentBytes := s.int32ToBytes(bet.Document)

	// Convert dynamic-length strings to bytes and calculate its length
	firstNameBytes := []byte(bet.FirstName)
	firstNameLenBytes := s.int16ToBytes(uint16(len(firstNameBytes)))

	lastNameBytes := []byte(bet.LastName)
	lastNameLenBytes := s.int16ToBytes(uint16(len(lastNameBytes)))

	// Assume BirthDate is always a 10 byte string
	birthDateBytes := []byte(bet.BirthDate)

	// Combine all byte slices into one
	data := append(opcodeBytes, documentBytes...)
	data = append(data, s.int16ToBytes(clientID)...)
	data = append(data, betNumberBytes...)
	data = append(data, birthDateBytes...)
	data = append(data, firstNameLenBytes...)
	data = append(data, firstNameBytes...)
	data = append(data, lastNameLenBytes...)
	data = append(data, lastNameBytes...)

	return data
}
