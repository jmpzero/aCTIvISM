"""
Continious Speedtesting script

"""

import argparse
import math
import os
import speedtest
import sqlite3
import sys

from operator import itemgetter
from collections import OrderedDict

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

def distance(origin, destination):
  lat1, lon1 = origin
  lat2, lon2 = destination
  radius = 6371 # km

  dlat = math.radians(lat2 - lat1)
  dlon = math.radians(lon2 - lon1)
  a = (math.sin(dlat/2)*math.sin(dlat/2)+
       math.cos(math.radians(lat1)) *
       math.cos(math.radians(lat2)) *
       math.sin(dlon/2) *
       math.sin(dlon/2))
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  d = radius * c
  return d


if __name__ == "__main__":

  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("-db", help="path and name of database")
  arg_parser.add_argument("-s",  help="server id of speedtest server, if not specified best server will be taken")
  arg_parser.add_argument("-list", help="lists servers in ascending order")
  args = arg_parser.parse_args()

  print args


  servers = []
  speed_api = speedtest.Speedtest()

  if args.list != None:
    servers = speed_api.get_servers()
    serv = []
    for s in servers:
      if (servers[s][0]['country'] != args.list):
        continue

      serv.append(dict())
      serv[-1]['id'] = servers[s][0]['id']
      serv[-1]['name'] = servers[s][0]['name']
      serv[-1]['country'] = servers[s][0]['country']
      serv[-1]['distance'] = distance((float(speed_api.results.dict()['client']['lat']), float(speed_api.results.dict()['client']['lon'])), (float(servers[s][0]['lat']), float(servers[s][0]['lon'])))

    for i in range(0,len(serv)):
      for j in range(i,len(serv)):
        if i == j:
          continue
        if serv[i] > serv[j]:
          tmp = serv[j]
          serv[j] = serv[i]
          serv[i] = tmp

    for x in serv:
      print "%s: %s, %s [%d km]"%(x['id'], x['name'], x['country'], x['distance'])
    exit(0)

  if args.db == None:
    print "ERROR: No database specified!"


  sql_connection = sqlite3.connect(args.db)

  if detect_database(args.db) == False:
    create_tables(sql_connection)

  max_id = get_max_id( sql_connection )

  servers = speed_api.get_servers()
  if args.s != None:
    key = ""
    for k, server in servers.items():
      if server[0]['id'] == args.s:
        key = k
    speed_api.get_best_server(servers[key])
  else:
    speed_api.get_best_server()
  speed_api.download()
  speed_api.upload()

  speed_api.results.share()

  r = speed_api.results.dict()

  download = float((r['download'] / 1000.0 / 1000.0))
  ping = int(round(r['ping'], 0))
  upload = float((r['upload'] / 1000.0 / 1000.0))

  print("Ping: %d ms" % ping )
  print("Download: %d MBit/s" % download )
  print("Upload: %d MBit/s" % upload )

  cursor = sql_connection.cursor()

  cursor.execute("insert into speedtest (id, bytes_sent, download, timestamp, share, bytes_received, ping, upload) VALUES (?,?,?,?,?,?,?,?)", (max_id, r['bytes_sent'], r['download'], r['timestamp'], r['share'], r['bytes_received'], r['ping'], r['upload']))

  cursor.execute("INSERT INTO CLIENT (cid, rating, loggedin, isprating, ispdlavg, ip, isp, lon, ispulavg, country, lat) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (max_id, r['client']['rating'], r['client']['loggedin'], r['client']['isprating'], r['client']['ispdlavg'], r['client']['ip'], r['client']['isp'], r['client']['lon'], r['client']['ispulavg'], r['client']['country'], r['client']['lat']))

  cursor.execute("insert into SERVER (sid, latency, name, url, country, lon, cc, host, sponsor, url2, lat, id, d) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (max_id, r['server']['latency'], r['server']['name'], r['server']['url'], r['server']['country'], r['server']['lon'], r['server']['cc'], r['server']['host'], r['server']['sponsor'], r['server']['url2'], r['server']['lat'], r['server']['id'], r['server']['d']))

  sql_connection.commit()


