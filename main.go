package main

import (
	"code.google.com/p/plotinum/plot"
	"code.google.com/p/plotinum/plotter"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"image/color"
	"log"
	"net/http"
	"strconv"
	"time"
)

type TickerData struct {
	Last   string
	High   string
	Low    string
	Vwap   string
	Volume string
	Bid    string
	Ask    string
}

func fetchBitstampTicker() (ticker *TickerData, err error) {
	var res *http.Response
	res, err = http.Get("https://www.bitstamp.net/api/ticker/")
	if err != nil {
		return
	}
	defer res.Body.Close()
	dec := json.NewDecoder(res.Body)
	ticker = new(TickerData)
	err = dec.Decode(ticker)
	if err != nil {
		ticker = nil
		return
	}
	return
}

func fetchBitstampMarketData() ([][]string, error) {
	res, err := http.Get("http://api.bitcoincharts.com/v1/trades.csv?symbol=bitstampUSD")
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	reader := csv.NewReader(res.Body)
	return reader.ReadAll()
}

func plotMarketData(data [][]string) {
	p, err := plot.New()
	if err != nil {
		panic(err)
	}
	pts := make(plotter.XYs, len(data))
	for i := len(data) - 1; i >= 0; i-- {
		pts[i].X, _ = strconv.ParseFloat(data[i][0], 64)
		pts[i].Y, _ = strconv.ParseFloat(data[i][1], 64)
	}
	l, err := plotter.NewLine(pts)
	if err != nil {
		panic(err)
	}
	l.LineStyle.Color = color.RGBA{A: 255}
	p.Add(l)
	p.Legend.Add("price", l)
	// Save the plot to a PNG file.
	if err := p.Save(4, 4, "points.png"); err != nil {
		panic(err)
	}
}

func main() {
	var ticker *TickerData
	var err error
	ticker, err = fetchBitstampTicker()
	if err != nil {
		log.Fatal("Error on fetching bitstamp ticker: " + err.Error())
	}
	fmt.Printf("Current bitstamp ticker data: %+v\n", *ticker)

	var data [][]string
	data, err = fetchBitstampMarketData()
	if err != nil {
		log.Fatal("Error on fetching bitstamp market data: " + err.Error())
	}
	plotMarketData(data)
	for i := len(data) - 1; i >= 0; i-- {
		row := data[i]
		unixtime, _ := strconv.ParseInt(row[0], 10, 64)
		t := time.Unix(unixtime, 0)
		fmt.Printf("%d: %s - %s %s\n", i, t, row[1], row[2])
	}
}
