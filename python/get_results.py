import xml.etree.cElementTree as etree
import urllib2

from StringIO import StringIO

sport_dict = {'NHL' : 'http://sportsfeeds.bovada.lv/basic/NHL.xml',
              'NBA' : 'http://sportsfeeds.bovada.lv/basic/NBA.xml',
              'NFL' : 'http://sportsfeeds.bovada.lv/basic/NFL.xml', 
              'NCB' : 'http://sportsfeeds.bovada.lv/basic/NCB.xml',
              'NTP' : 'http://sportsfeeds.bovada.lv/basic/NTP.xml'};
              

class result_parser():
    
    def get_results(self, sport):
        xmlFile = sport_dict[sport]
        theFile = urllib2.urlopen(xmlFile)
        xml = theFile.read()
        theFile.close()
    
        tree = etree.iterparse(StringIO(xml))
        main_dict = {}  # Key = eventID, Value = {competitor: score}
    
        for index, dates in tree:
            events = list(dates)
            for event_elem in events:
                game_status = event_elem.get("GAME_STATUS")
                if game_status:
                    if game_status == "Final":
                        scores_dict = {}
                        id = event_elem.get("ID")
                        if id: 
                            main_dict[id] = scores_dict
                            ev_info_elems = list(event_elem)
                            for ev_info_elem in ev_info_elems:
                                if ev_info_elem.tag == "Competitor":
                                    name = ev_info_elem.get("NAME")
                                    score = ev_info_elem.get("SCORE")
                                    if name and score:
                                        scores_dict[name] = score
                                        
        return main_dict     
        
      
                   
                            