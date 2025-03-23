package common

import (
	"net"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

const AckOpcode = 0

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// WriteAll ensures that all bytes are written to the connection
func WriteAll(conn net.Conn, data []byte) error {
	totalSent := 0
	for totalSent < len(data) {
		sent, err := conn.Write(data[totalSent:])
		if err != nil {
			return err
		}
		totalSent += sent
	}
	log.Infof("action: send_bytes | result: success | bytes_sent: %v", totalSent)
	return nil
}

// ReadAll ensures that exactly 'size' bytes are read from the connection
func ReadAll(conn net.Conn, size int) ([]byte, error) {
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

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop(bet Bet) {

	c.createClientSocket()
	sigc := make(chan os.Signal, 1)
	signal.Notify(sigc, syscall.SIGTERM)
	go func() {
		<-sigc
		c.conn.Close()
		log.Infof("action: close | result: success | resource type: client socket | client_id: %v",
			c.config.ID)
		os.Exit(0)
	}()

	serializer := new(Serializer)
	configID, _ := strconv.Atoi(c.config.ID)

	betBytes := serializer.SerializeBet(bet, uint16(configID))

	// Ensure betBytes has a length of 150 bytes by padding it with 0s in case its shorter
	if len(betBytes) > 150 {
		log.Errorf("action: serialize_bet | result: fail | client_id: %v | error: bet fields are too long", c.config.ID)
		c.conn.Close()
		return
	} else if len(betBytes) < 150 {
		padding := make([]byte, 150-len(betBytes))
		betBytes = append(betBytes, padding...)
	}

	if err := WriteAll(c.conn, betBytes); err != nil {
		log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		c.conn.Close()
		return
	}

	buffer, err := ReadAll(c.conn, 2)
	if err != nil {
		log.Errorf("action: read_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		c.conn.Close()
		return
	}
	responseOpcode := serializer.deserializeOpcode(buffer)
	if responseOpcode == AckOpcode {
		log.Infof("action: apuesta_enviada | result: success | dni: %s | numero: %v", bet.Document, bet.Number)
	}

	c.conn.Close()

	log.Infof("action: received_data | result: success | client_id: %v | data: %v", c.config.ID, buffer)

	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
