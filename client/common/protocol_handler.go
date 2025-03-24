package common

import "net"

type ProtocolHandler struct {
	messenger  *Messenger
	connection net.Conn
	clientID   uint16
}

const AckOpcode = 0
const BatchErrorOpcode = 2

func NewProtocolHandler(conn net.Conn, clientID uint16) *ProtocolHandler {
	return &ProtocolHandler{
		messenger:  NewMessenger(),
		connection: conn,
		clientID:   clientID,
	}
}

func (p *ProtocolHandler) SendBetsAndPrintLogs(bets []Bet, batchNumber int) {

	send_bet_err := p.messenger.SendBets(p.connection, bets, p.clientID)

	if send_bet_err != nil {
		log.Errorf("action: send_bets | result: fail | client_id: %v | error: %v",
			p.clientID,
			send_bet_err.Error(),
		)
	}

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

	log.Infof("action: loop_finished | result: success | client_id: %v", p.clientID)
}

func (p *ProtocolHandler) SendEndOfBets() {
	p.messenger.SendEndOfBets(p.connection, p.clientID)
}
