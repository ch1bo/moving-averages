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
	"os/exec"
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

type MarketDataPoint struct {
	Time time.Time
	BTC  float64
	USD  float64
}

func fetchBitstampMarketData() ([]MarketDataPoint, error) {
	res, err := http.Get("http://api.bitcoincharts.com/v1/trades.csv?symbol=bitstampUSD")
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	reader := csv.NewReader(res.Body)
	csvData, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}
	data := make([]MarketDataPoint, len(csvData))
	for i, row := range csvData {
		t, err := strconv.ParseInt(row[0], 10, 64)
		if err != nil {
			panic(err)
		}
		data[i].Time = time.Unix(t, 0)
		data[i].BTC, _ = strconv.ParseFloat(row[1], 64)
		data[i].USD, _ = strconv.ParseFloat(row[2], 64)
	}
	return data, nil
}

func plotMarketData(data []MarketDataPoint, filename string) {
	p, err := plot.New()
	if err != nil {
		panic(err)
	}
	p.X.Tick.Marker = func(min, max float64) []plot.Tick {
		fmt.Printf("should create tick for min=%v max=%v\n", min, max)
		return []plot.Tick{
			plot.Tick{
				Value: min,
				Label: time.Unix(int64(min), 0).Format(time.Stamp),
			},
			plot.Tick{
				Value: max,
				Label: time.Unix(int64(max), 0).Format(time.Stamp),
			},
		}
	}
	pts := make(plotter.XYs, len(data))
	for i := len(data) - 1; i >= 0; i-- {
		pts[i].X = float64(data[i].Time.Unix())
		pts[i].Y = data[i].BTC
	}
	l, err := plotter.NewLine(pts)
	if err != nil {
		panic(err)
	}
	l.LineStyle.Color = color.RGBA{A: 255}
	p.Add(l)
	p.Legend.Add("price", l)
	p.Add(plotter.NewGrid())
	// Save the plot to a PNG file.
	if err := p.Save(14, 10, filename); err != nil {
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

	data, err := fetchBitstampMarketData()
	if err != nil {
		log.Fatal("Error on fetching bitstamp market data: " + err.Error())
	}
	plotMarketData(data, "points.svg")
	// for i := len(data) - 1; i >= 0; i-- {
	// 	row := data[i]
	// 	unixtime, _ := strconv.ParseInt(row[0], 10, 64)
	// 	t := time.Unix(unixtime, 0)
	// 	fmt.Printf("%d: %s - %s %s\n", i, t, row[1], row[2])
	// }
	exec.Command("eog", "points.svg").Start()
}
