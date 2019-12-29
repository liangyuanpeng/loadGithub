from optparse import OptionParser

# [...]
def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="write report to FILE", metavar="FILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    (options, args) = parser.parse_args()
    print(options)
if __name__ == "__main__":
    main()

#ffmpeg -re -i mapReduce.mp3 -codec:v libx264 -codec:a copy -map 0 -f hls  -hls_list_size 6  -hls_time 15 playlist.m3u8