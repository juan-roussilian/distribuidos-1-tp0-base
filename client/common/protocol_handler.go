package common

import "net"

type ProtocolHandler struct {
	messenger *Messenger
}

func NewProtocolHandler() *ProtocolHandler {
	return &ProtocolHandler{
		messenger: NewMessenger(),
	}
}

func (p *ProtocolHandler) SendBetAndPrintLogs(connection net.Conn, bet Bet, clientID uint16) {

	send_bet_err := p.messenger.SendBet(connection, bet, clientID)

	if send_bet_err != nil {
		log.Errorf("action: send_bet | result: fail | client_id: %v | error: %v",
			clientID,
			send_bet_err.Error(),
		)
	}

	responseOpcode, rec_bet_err := p.messenger.ReceiveResult(connection, clientID)

	if rec_bet_err != nil {
		log.Errorf("action: read_message | result: fail | client_id: %v | error: %v",
			clientID,
			rec_bet_err.Error(),
		)
	}

	if responseOpcode == AckOpcode {
		log.Infof("action: send_bet | result: success | dni: %v | numero: %v", bet.Document, bet.Number)
	}

	log.Infof("action: loop_finished | result: success | client_id: %v", clientID)
}
