package common

import "net"

type ProtocolHandler struct {
	messenger  *Messenger
	connection net.Conn
	clientID   uint16
}

const AckOpcode = 0
const SendBetBatchOpcode = 1
const BatchErrorOpcode = 2
const EndOfBatchOpcode = 3
const AskWinnersOpcode = 4
const WinnersOpcode = 5

func NewProtocolHandler(conn net.Conn, clientID uint16) *ProtocolHandler {
	return &ProtocolHandler{
		messenger:  NewMessenger(),
		connection: conn,
		clientID:   clientID,
	}
}

func (p *ProtocolHandler) RunProtocol(bets []Bet, maxAmount int) {
	// Flow control for the entire protocol
	p.SplitAndSendBets(bets, maxAmount)
	p.SendEndOfBets()
	winners := p.AskForWinners()
	log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v | ganadores: %v", len(winners), winners)
	log.Infof("action: loop_finished | result: success | client_id: %v", p.clientID)
}

func (p *ProtocolHandler) SplitAndSendBets(bets []Bet, maxAmount int) {
	// Split bets into batches and send them while handling server response
	for i := 0; i < len(bets); i += maxAmount {
		end := i + maxAmount
		if end > len(bets) {
			end = len(bets)
		}
		currentBets := bets[i:end]
		batchNumber := i/maxAmount + 1

		// Send bets and handle responses
		p.SendBets(currentBets, batchNumber)
		responseOpcode, rec_bet_err := p.messenger.ReceiveResult(p.connection, p.clientID)

		if rec_bet_err != nil {
			log.Errorf("action: read_message | result: fail | client_id: %v | error: %v",
				p.clientID,
				rec_bet_err.Error(),
			)
		}

		if responseOpcode == AckOpcode {
			log.Infof("action: apuestas_enviadas | result: success | cantidad: %v | numero_lote: %v", len(bets), batchNumber)
		} else if responseOpcode == BatchErrorOpcode {
			log.Errorf("action: apuestas_enviadas | result: fail | cantidad: %v | numero_lote: %v", len(bets), batchNumber)
		}
	}
}

func (p *ProtocolHandler) SendBets(bets []Bet, batchNumber int) {

	send_bet_err := p.messenger.SendBets(p.connection, bets, p.clientID)

	if send_bet_err != nil {
		log.Errorf("action: send_bets | result: fail | client_id: %v | error: %v",
			p.clientID,
			send_bet_err.Error(),
		)
	}
}

func (p *ProtocolHandler) SendEndOfBets() {
	p.messenger.SendEndOfBets(p.connection, p.clientID)
}

func (p *ProtocolHandler) AskForWinners() []uint16 {
	p.messenger.AskForWinners(p.connection, p.clientID)
	return p.messenger.ReceiveWinners(p.connection)
}
