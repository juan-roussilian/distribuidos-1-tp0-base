package common

import (
	"encoding/csv"
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"
)

func ParseBetsFromCSV(filePath string, startRow uint, numRows uint) ([]Bet, error) {

	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	reader.Comma = ','

	var bets []Bet
	var currentRow uint = 0
	for {
		row, err := reader.Read()
		if err != nil {
			if err == io.EOF {
				break
			}
			return nil, fmt.Errorf("failed to read CSV: %w", err)
		}

		if currentRow < startRow {
			currentRow++
			continue
		}

		if currentRow >= startRow+numRows {
			break
		}

		bet, err := parseBet(row, currentRow+1)
		if err != nil {
			return nil, err
		}
		bets = append(bets, bet)

		currentRow++
	}

	return bets, nil
}

func parseBet(row []string, lineNumber uint) (Bet, error) {
	document, err := strconv.Atoi(strings.TrimSpace(row[2]))
	if err != nil {
		return Bet{}, fmt.Errorf("invalid document at line %d: %v", lineNumber, err)
	}

	betNumber, err := strconv.Atoi(strings.TrimSpace(row[4]))
	if err != nil {
		return Bet{}, fmt.Errorf("invalid bet number at line %d: %v", lineNumber, err)
	}

	bet := Bet{
		FirstName: strings.TrimSpace(row[0]),
		LastName:  strings.TrimSpace(row[1]),
		Document:  uint32(document),
		BirthDate: strings.TrimSpace(row[3]),
		Number:    uint16(betNumber),
	}

	return bet, nil
}
