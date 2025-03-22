package common

package main

import (
	"encoding/binary"
	"fmt"
	"net"
)


const SendBetOpcode = 0

type Serializer struct{}

// Convert an int16 to a 2-byte slice
func (s *Serializer) int16ToBytes(n int16) []byte {
	b := make([]byte, 2)
	binary.BigEndian.PutUint16(b, uint16(n))
	return b
}

// Convert an int32 to a 4-byte slice
func (s *Serializer) int32ToBytes(n int32) []byte {
	b := make([]byte, 4)
	binary.BigEndian.PutUint16(b, uint32(n))
	return b
}


// Serialize a Bet object into a byte slice
func (s *Serializer) SerializeBet(bet Bet) []byte {
	
	// Convert integers values  to bytes
	opcodeBytes := s.int16ToBytes(SendBetOpcode)
	betNumberBytes := s.int16ToBytes(bet.Number)
	documentBytes := s.int32ToBytes(bet.Document)

	// Convert dynamic-length strings to bytes and calculate its length
	firstNameBytes := []byte(bet.FirstName)
	firstNameLenBytes := s.intToBytes(int16(len(firstNameBytes)))

	lastNameBytes := []byte(bet.LastName)
	lastNameLenBytes := s.intToBytes(int16(len(lastNameBytes)))

	// Assume BirthDate is always a 10 byte string
	birthDateBytes := []byte(bet.BirthDate)


	// Combine all byte slices into one
	data := append(opcodeBytes, documentBytes...)
	data = append(data, betNumberBytes)
	data = append(data, birthDateBytes...) 
	data = append(data, firstNameLenBytes...)        
	data = append(data, firstNameBytes...)      
	data = append(data, lastNameLenBytes...)      
	data = append(data, lastNameBytes...)    

	return data
}

func main() {
	// Example bet object
	bet := Bet{
		Opcode:      1,
		Document:    12345,
		Nombre:      "Juan",
		Apellido:    "Perez",
		FixedString: "ABCDEFGHIJ",
	}

	// Create serializer
	serializer := Serializer{}

	// Serialize the bet object
	data := serializer.Serialize(bet)

	// Connect to the TCP server
	conn, err := net.Dial("tcp", "localhost:12345")
	if err != nil {
		fmt.Println("Error connecting:", err)
		return
	}
	defer conn.Close()

	// Send the serialized bytes
	_, err = conn.Write(data)
	if err != nil {
		fmt.Println("Error sending data:", err)
		return
	}

	fmt.Println("Sent data successfully")
}
