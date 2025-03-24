package common

import (
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
	"strings"
)

func ParseBetsFromCSV(filePath string) ([]Bet, error) {

	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	reader.Comma = ','

	rows, err := reader.ReadAll()
	if err != nil {
		return nil, fmt.Errorf("failed to read CSV: %w", err)
	}

	var bets []Bet
	for i, row := range rows {

		document, err := strconv.Atoi(strings.TrimSpace(row[2]))
		if err != nil {
			return nil, fmt.Errorf("invalid document at line %d: %v", i+1, err)
		}

		betNumber, err := strconv.Atoi(strings.TrimSpace(row[4]))
		if err != nil {
			return nil, fmt.Errorf("invalid bet number at line %d: %v", i+1, err)
		}

		bet := Bet{
			FirstName: strings.TrimSpace(row[0]),
			LastName:  strings.TrimSpace(row[1]),
			Document:  uint32(document),
			BirthDate: strings.TrimSpace(row[3]),
			Number:    uint16(betNumber),
		}
		bets = append(bets, bet)
	}

	return bets, nil
}
