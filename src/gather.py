"""
Continious Speedtesting script

"""

import os
import sys
import speedtest
import sqlite3

def create_tables(connection):
  cursor = connection.cursor()
  cursor.execute("CREATE TABLE CLIENT (cid, rating, loggedin, isprating, ispdlavg, ip, isp, lon, ispulavg, country, lat)")
  cursor.execute("CREATE TABLE SERVER (sid, latency, name, url, country, lon, cc, host, sponsor, url2, lat, id, d)")
  cursor.execute("CREATE TABLE speedtest (id, bytes_sent, download, timestamp, share, bytes_received, ping, upload)")
  connection.commit()

def detect_database(name):
  if os.path.isfile(name):
    if os.path.getsize(name) > 100:
      #with open(name, 'r', encoding = "ISO-8859-1") as f:
      with open(name, 'r') as f:
        header = f.read(100)
        if header.startswith('SQLite format 3'):
          return True

  return False


def get_max_id( connection ):
  cursor = connection.cursor()
  cursor.execute('SELECT max(id) from speedtest')
  id = cursor.fetchone()
  if id[0]== None:
    return 0
  return id[0]+1

if __name__ == "__main__":

  servers = []
  speed_api = speedtest.Speedtest()

  sql_connection = sqlite3.connect('speedtest.db')

  if detect_database('speedtest.db') == False:
    create_tables(sql_connection)

  max_id = get_max_id( sql_connection )

  speed_api.get_servers(servers)
  speed_api.get_best_server()
  speed_api.download()
  speed_api.upload()

  speed_api.results.share()

  r = speed_api.results.dict()

  print servers


  download = float((r['download'] / 1000.0 / 1000.0))
  ping = int(round(r['ping'], 0))
  upload = float((r['upload'] / 1000.0 / 1000.0))

  print("Ping: %d ms" % ping )
  print("Download: %d MBit/s" % download )
  print("Upload: %d MBit/s" % upload )

  cursor = sql_connection.cursor()

  cursor.execute("insert into speedtest (id, bytes_sent, download, timestamp, share, bytes_received, ping, upload) VALUES (?,?,?,?,?,?,?,?)", (max_id, r['bytes_sent'], r['download'], r['timestamp'], r['share'], r['bytes_received'], r['ping'], r['upload']))

  cursor.execute("INSERT INTO CLIENT (cid, rating, loggedin, isprating, ispdlavg, ip, isp, lon, ispulavg, country, lat) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (max_id, r['client']['rating'], r['client']['loggedin'], r['client']['isprating'], r['client']['ispdlavg'], r['client']['ip'], r['client']['isp'], r['client']['lon'], r['client']['ispulavg'], r['client']['country'], r['client']['lat']))

  #print r['server']
  cursor.execute("insert into SERVER (sid, latency, name, url, country, lon, cc, host, sponsor, url2, lat, id, d) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (max_id, r['server']['latency'], r['server']['name'], r['server']['url'], r['server']['country'], r['server']['lon'], r['server']['cc'], r['server']['host'], r['server']['sponsor'], r['server']['url2'], r['server']['lat'], r['server']['id'], r['server']['d']))

  sql_connection.commit()


