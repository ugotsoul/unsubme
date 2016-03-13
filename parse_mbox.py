import mailbox, csv, re, time, quopri
from BeautifulSoup import BeautifulSoup, SoupStrainer

t0 = time.clock()
unsubscribe_links = {}
no_unsubscribe_links_found = {}
log_errors = 0

def process_mail():
    for message in mailbox.mbox('promo_label.mbox'):
        body = message.get_payload(decode=True)

        if not body:
            body = message.get_payload()[0].get_payload(decode=True)
        # Stringify xml / hxml for BeautifulSoup: otherwise it will error and be unable to detect encoding
        if type(body) is not str:
            body = str(body)

        for link in BeautifulSoup(body, parseOnlyThese=SoupStrainer('a', href=True)):
            if link and link.get('href'):
                parse_links(link, message['from'])

def parse_links(link, msg_from):
    if re.search(r'(unsub|subscri)', str(link.text.encode('ascii', 'ignore')).lower())
        email_address = re.search(r'<([^>]+)', msg_from).group(1)
        if email_address not in unsubscribe_links:
            unsubscribe_links[email_address] = [link.get('href'), re.search(r'^"(.+)["]|^(.+)[<]', msg_from).group(1)]
            return
    else:
        no_unsubscribe_links_found[email_address] = link


# create and write links to csv
def write_csv(link_dict):
    f = open("test.csv", "wb")
    fieldnames = ['email_address', 'unsubscribe_link', 'source']
    writer = csv.DictWriter(open("test.csv", "wb"), fieldnames=fieldnames)
    writer.writeheader()

    for key in link_dict:
        writer.writerow({
            'email_address': key,
            'unsubscribe_link': link_dict[key][0],
            'source': link_dict[key][1]
            })

def main():
    process_mail()
    write_csv(unsubscribe_links)

    print "*************************************\n"
    print "Unsubscribe Links found: %d" % len(unsubscribe_links)
    print "Number of no links found: %d" % log_errors
    print "script time: %d seconds" % (time.clock() - t0)
    print "\n*************************************"

if __name__ == '__main__':
    main()
