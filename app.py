import curses, json, urllib.request, urllib.parse, codecs, subprocess
import logging
from window import Window
from lib import parse_top

print("[afreeca-curses] initializing")
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
curses.curs_set(0)

SEARCH_API = "http://sch.afreecatv.com/api.php?nListCnt=10&szKeyword=SEARCH_WORD="
ALL_API = "http://live.afreecatv.com:8057/api/main_broad_list_api.php?selectType=action&selectValue=all&orderType=view_cnt&pageNo=1type=json"
PLAYER_URL = "http://play.afreecatv.com/"

quality = "best"

def query_afreeca(query=""):
    if query:
        query = urllib.parse.quote(query)
        url = SEARCH_API+query
    else:
        query = urllib.parse.quote(query)
        url = ALL_API
    with urllib.request.urlopen(url) as response:
        res = response.read()
        res = res[1:len(res)-2]
        # print(res)
        return json.loads(res.decode('utf-8'))

key = 0

try:
    win = Window(stdscr)
    data = query_afreeca()
    cache = data
    while key != ord('q') and key != ord('Q'):
        if win.size[0] < 10 or win.size[1] < 32:
            stdscr.clear()
            stdscr.addstr(0,0,"Terminal")
            stdscr.addstr(1,0,"too small")
        else:
            win.reset_window()
            if win.state == "top":
                totalitems = len(data['broad'])
                currentpage = data['broad'][win.maxitems*win.page:win.maxitems*(win.page+1)]

                for i, v in enumerate(currentpage):
                    if i < win.maxitems:
                        if i == win.highlight:
                            win.win_l.addnstr(i * 2 + 2, 2, str(v["user_nick"]), win.maxlen, curses.A_REVERSE)

                            # Title of broadcast
                            if len(str(v["broad_title"])) > win.maxlen:
                                win.win_r.addnstr(2, 3, str(v["broad_title"])[:win.maxlen - 3] + "...", win.maxlen)
                                # win.win_r.addnstr(2, 3, "EXCEEDED", win.maxlen)
                            else:
                                win.win_r.addnstr(2, 3, str(v["broad_title"]), win.maxlen)

                            win.win_r.addnstr(4, 3, "Viewers: " + str(v["total_view_cnt"]), win.maxlen)
                        else:
                            win.win_l.addstr(i * 2 + 2, 2, str(v["user_nick"]), win.maxlen)

        win.win_l.refresh()
        win.win_r.refresh()
        key = stdscr.getch()

        # Key movements
        if key == curses.KEY_DOWN or key == ord("j"):
            win.move_down(totalitems)

        elif key == curses.KEY_UP or key == ord("k"):
            win.move_up(totalitems)
        
        elif key == curses.KEY_RIGHT or key == 10 or key == ord("l"):
            curses.nocbreak(); stdscr.keypad(0); curses.echo()
            curses.endwin()
            print("[afreeca-curses] Launching streamlink")
            selected_data = data['broad'][win.highlight + win.page * win.maxitems]
            ls_exit_code = subprocess.call(["streamlink", PLAYER_URL + selected_data["user_id"] + "/" + selected_data["broad_no"], quality])
            while ls_exit_code != 0:
                logging.fatal("\nStreamlink has encountered an error")
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(1)
            win = Window(stdscr)

        # Refresh list of streams
        elif key == ord('r') or key == ord('R'):
            win = Window(stdscr)
            data = query_afreeca()
            cache = data
            win.reset_window()

except Exception as e:
    logging.fatal(e)

finally:
    curses.nocbreak(); stdscr.keypad(0); curses.echo()
    curses.endwin()
    print("[afreeca-curses] exiting")
