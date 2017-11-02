import xml.etree.cElementTree as etree
import urllib2

from StringIO import StringIO

sport_dict = {'NHL' : 'http://sportsfeeds.bovada.lv/basic/NHL.xml',
              'NBA' : 'http://sportsfeeds.bovada.lv/basic/NBA.xml',
              'NFL' : 'http://sportsfeeds.bovada.lv/basic/NFL.xml', 
              'NCB' : 'http://sportsfeeds.bovada.lv/basic/NCB.xml',
              'NTP' : 'http://sportsfeeds.bovada.lv/basic/NTP.xml', 
              'MLB' : 'http://sportsfeeds.bovada.lv/basic/MLB.xml'};


def make_line(line_elem, event_dict, k):
    choice_elem = line_elem.find("Choice")
    #odds_elem = line_elem.find("Odds")
    
    if line_elem.get("TYPE") == "Moneyline":

        if choice_elem is not None:
            return choice_elem.get("VALUE")
        
    else: #get the spread numbers
        if choice_elem is not None: 
            spread =  choice_elem.get("VALUE")
            spread.encode('utf-8')
            return spread
    
    return None

class sport_parser():
    
    def parseXML(self, sport):
     
        xmlFile = sport_dict[sport]
        theFile = urllib2.urlopen(xmlFile)
        xml = theFile.read()
        theFile.close()
    
        tree = etree.iterparse(StringIO(xml))
        main_dict = {}

        i = 0
        for index, dates in tree:
            if dates.tag == "Date":
                date_dict = {} 
                date_dict['date'] = dates.get("DTEXT")
                main_dict['date_' + str(i) ] = date_dict
                events = list(dates)
                j = 0
                for event_elem in events:      
                    event_dict = {}
                    event_dict['ID'] = event_elem.get("ID")
                    event_dict['game_status'] = event_elem.get("STATUS")
         
                    time_elem = event_elem.find("Time")
                                       
                    if time_elem is not None:
                        event_dict['time'] = time_elem.get("TTEXT")
                    
                    ev_info_elems = list(event_elem)  # Look through the elements for this event.
                    k = 0
                    for ev_info_elem in ev_info_elems:
                        competitor_dict = {}
                        if ev_info_elem.tag == "Competitor":
                            competitor_dict['name'] = ev_info_elem.get("NAME")
                            competitor_dict['score'] = ev_info_elem.get("SCORE")
                            event_dict['competitor_' + str(k)] = competitor_dict
                            
                            compet_elems = list(ev_info_elem)  # This event_elem is a competitor and therefore has lines
                            for compet_elem in compet_elems: 
                                if compet_elem.tag == "Line":  # We only care about Lines in the competitor class
                                    if compet_elem.get("TYPE") == "Moneyline":
                                        moneyline_dict = make_line(compet_elem, event_dict, k)
                                        if moneyline_dict:
                                            event_dict['competitor_' + str(k)]['moneyline'] = moneyline_dict
                                    else:
                                        spread_dict = make_line(compet_elem, event_dict, k)
                                        if spread_dict:
                                            event_dict['competitor_' + str(k)]['spread'] = spread_dict

                        k+=1 
                    main_dict['date_' + str(i)]['event_' + str(j)] = event_dict     

                    j+=1
                i+=1
        return main_dict      

