import argparse
import re
import sqlite3


def gen_daily_results(template, requested_date, cursor):
  cursor.execute("""
      select
        date(s.timestamp),
        time(s.timestamp),
        s.ping,
        s.download,
        s.upload,
        c.ip,
        srv.name,
        srv.url,
        srv.country,
        srv.sponsor,
        srv.url2
      from
        speedtest as s,
        CLIENT as c,
        SERVER as srv
      where
        s.id = c.cid
        AND s.id = srv.sid
        AND date(s.timestamp) = ?
        """, requested_date)
  rows = cursor.fetchall()

  single_results = []
  label = []
  data_download = []
  data_upload = []
  cnt = 0
  avg_dl = 0
  avg_ul = 0
  avg_ping = 0

  avg = []
  avgul = []

  for r in rows:
    label.append(str(r[1]))

    data_download.append(r[3] / 1000.0 / 1000.0)
    data_upload.append(r[4] / 1000.0 / 1000.0 )
    single_results.append("<tr>")
    single_results.append("<td>"+r[0]+"</td>")
    single_results.append("<td>"+r[1]+"</td>")
    single_results.append("<td>"+str(r[2])+"</td>")
    single_results.append("<td>"+str(r[3])+"</td>")
    single_results.append("<td>"+str(r[4])+"</td>")
    single_results.append("<td>"+r[5]+"</td>")
    single_results.append("<td>"+r[6]+"</td>")
    single_results.append("<td>"+r[8]+"</td>")
    single_results.append("<td>"+r[9]+"</td>")
    single_results.append("</tr>")
    avg_dl = avg_dl + r[3]
    avg_ul = avg_ul + r[4]
    avg_ping = avg_ping + r[2]
    cnt = cnt + 1

    if len(avgul) == 0:
      avgul.append(r[4]/1000.0/1000.0)
      avgul.append(r[4]/1000.0/1000.0)
      avgul.append(r[4]/1000.0/1000.0)
      avgul.append(r[4]/1000.0/1000.0)
      avgul.append(r[4]/1000.0/1000.0)
    else:
      avgul.append( (avgul[-4] + avgul[-3] + avgul[-2] + avgul[-1] + r[4]/1000.0/1000.0) / 5 )

    if len(avg) == 0:
      avg.append(r[3]/1000.0/1000.0)
      avg.append(r[3]/1000.0/1000.0)
      avg.append(r[3]/1000.0/1000.0)
      avg.append(r[3]/1000.0/1000.0)
      avg.append(r[3]/1000.0/1000.0)
    else:
      avg.append( (avg[-4] + avg[-3] + avg[-2] + avg[-1] + r[3]/1000.0/1000.0) / 5 )

  avg_dl = round(avg_dl / cnt / 1000.0 /1000.0, 3)
  avg_ul = round(avg_ul / cnt / 1000.0 / 1000.0, 3)
  avg_ping = round(avg_ping / cnt, 0)

  results = re.sub("SINGLE RESULTS", "".join(single_results), template)
  results = re.sub("PING", str(avg_ping) + " ms", results)
  results = re.sub("DL", str(avg_dl) + " MBit/s", results)
  results = re.sub("UL", str(avg_ul) + " MBit/s", results)
  results = re.sub("LABELS", str(label), results)
  results = re.sub("DATADOWNLOAD", str(data_download), results)
  results = re.sub("DATAUPLOAD", str(data_upload), results)
  results = re.sub("AVGDOWNLOAD", str(avg[4:]), results)
  results = re.sub("AVGUPLOAD", str(avgul[4:]), results)
  results = re.sub("DATE", requested_date, results)


  of = open(results_directory + "results_"+requested_date[0]+".html", "w")
  of.write(results)
  of.close()

  return avg_dl, avg_ul, avg_ping


if __name__ == '__main__':

  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("-db", help="database name")
  arg_parser.add_argument("-template_dir", help="directory where the templates are")
  arg_parser.add_argument("-results_dir", help="directory where the results will be saved")
  args = arg_parser.parse_args()

  results_directory = "../results/"
  template_directory = "../templates/"

  if args.results_dir != None:
    results_directory = args.results_dir + "/"

  if args.template_dir != None:
    template_directory = args.template_dir + "/"

  template_file_name = template_directory + "results.html"
  template_all_file_name = template_directory + "index.html"

  if args.db == None:
    print "ERROR: no database specified!"
    exit(-1)

  tf = open(template_file_name, 'r')
  template = tf.read()
  tf.close()

  tf = open(template_all_file_name, 'r')
  overall_template = tf.read()
  tf.close()

  sql_connection = sqlite3.connect(args.db)

  cursor = sql_connection.cursor()

  cursor.execute("""
    select distinct(date(timestamp)) from speedtest
    """)

  rows = cursor.fetchall()

  daily_dl = []
  daily_ul = []
  daily_ping = []
  daily_results = []
  labels = []
  avg_dl = 0
  avg_ul = 0
  avg_ping = 0
  cnt = 0

  for r in rows:
    (dl, ul, ping) = gen_daily_results(template, r, cursor)
    daily_dl.append(dl)
    daily_ul.append(ul)
    daily_ping.append(ping)
    avg_dl = avg_dl + dl
    avg_ul = avg_ul + ul
    avg_ping = avg_ping + ping
    cnt = cnt + 1
    labels.append(str(r[0]))

    daily_results.append("<tr>")
    daily_results.append("<td>" + str(r[0]) + "</td>")
    daily_results.append("<td>" + str(ping) + "</td>")
    daily_results.append("<td>" + str(dl) + "</td>")
    daily_results.append("<td>" + str(ul) + "</td>")
    daily_results.append("<td><a href=\"results_"+str(r[0])+".html\">results_"+str(r[0])+".html</a></td>")
    daily_results.append("</tr>")

  avg_dl = avg_dl / cnt
  avg_ul = avg_ul / cnt
  avg_ping = avg_ping / cnt


  results = overall_template
  results = re.sub("PING", str(avg_ping) + " ms", results)
  results = re.sub("DL", str(avg_dl) + " MBit/s", results)
  results = re.sub("UL", str(avg_ul) + " MBit/s", results)
  results = re.sub("LABELS", str(labels), results)
  results = re.sub("DATADOWNLOAD", str(daily_dl), results)
  results = re.sub("DATAUPLOAD", str(daily_ul), results)
  results = re.sub("DAILY_RES", str("".join(daily_results)), results)

  of = open(results_directory + "results.html", "w")
  of.write(results)
  of.close()

