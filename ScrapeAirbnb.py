# -*- coding: utf-8 -*-
"""
Created on Sat march 21 20:29:41 2016

@author: Balachandhar TN
Scraping Airbnb
"""

import mechanize
import cookielib
from lxml import html
import csv
import cStringIO
import codecs
from random import randint
from time import sleep
from lxml.etree import tostring
import bs4
import sys
import argparse
import time
import json
import urllib
import requests
from re import findall
from sets import Set

# Browser
br = mechanize.Browser()


#learned necessary configuration from

# Allow cookies
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
#specify browser to emulate
br.addheaders = [('User-agent',
'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]



#######################################
#  Wrapper Functions    ###############
#######################################

def IterateMainPage(location_string, loop_limit_str):
    MainResults = []
    """
    input:
        location_string (string) - this is a location string that conforms to the
                                   pattern on airbnb for example,
                                   Cambridge, MA is "Cambridge--MA"
        loop_limit (integer) -    this is the maximum number of pages you want to parse.

    output:
        list of dictionaries, with each list element corresponding to a unique listing

    This function iterates through the main listing pages where different properties
    are listed and there is a map, and collects the list of properties available along
    with the limited amount of information that is available in that page.  This function
    returns a list of dictionaries with each list element corresponding to a unique listing.
    Other functions will take the output from this function and iterate over them to explore
    the details of individual listings.
    """

    base_url = 'https://www.airbnb.ca/s/'
    page_url = '?page='
    location_string_change = str(location_string)
    loop_limit = int(loop_limit_str)

    try:
        for n in range(1, loop_limit+1):
            # 111 print 'Processing Main Page %s out of %s' % (str(n), str(loop_limit))
            #Implement random time delay for scraping
            sleep(randint(0,2))
            current_url = ''.join([base_url, location_string_change, page_url, str(n)])
            #print current_url
            MainResults += ParseMainXML(current_url, n)
           

    except:
        print 'This URL did not return results:', sys.exc_info()[0]

    #print 'Done Processing Main Page'
    return MainResults




#######################################
#  Main Page    #######################
#######################################


def ParseMainXML(url= 'https://www.airbnb.ca/s/Halifax--NS--Canada', pg = 0):

    """
    input: url (string )

            this is the url for the type of listings you want to search.
            default is to use the generic url to search for listings
            in Halifax, Canada
    input: pg (integer)

            this is an integer corresponding to the page number, this is meant
            to be passed in by the wrapper function and collected in the dictionary.

    output: dict
    ------
    This funciton parses the main page with mulitple airbnb listings, and
    returns a list of dictionaries corresponding to the attributes found
    """
    n = 1
    ListingDB = []
    
    try:
 
        tree = html.fromstring(br.open(url).get_data())
        print(tree)
        id_set = set()
        
        pdata = findall("<script type=\"application/json\"(.*)</script>", html.tostring(tree))
        id_value_now = []
        id_set.clear()
        for item in pdata:
            #print(item)
            #item_inside = findall("[0-9]+",item)
            #print item_inside
            item_inside = findall("\"extra_host_languages\":\[.*?\],\"id\":[0-9]+,\"instant_bookable\":",item)
            
            for id_val in item_inside:
                id_value_now =  findall("\d+", id_val)
                for id_set_one in id_value_now:
                    #dat['ListingID'] = id_val
                    #print id_val
                    id_set.add(id_set_one)
                            
            for id_set_val_index in id_set:        
                lat_note = findall("\"extra_host_languages\":\[.*?\],\"id\":%s,\"instant_bookable\":[a-z]+,\"is_business_travel_ready\":[a-z]+,\"is_new_listing\":[a-z]+,\"lat\":[0-9]+.[0-9]+,\"lng\":" %id_set_val_index,item)
                long_note = findall("\"extra_host_languages\":\[.*?\],\"id\":%s,\"instant_bookable\":[a-z]+,\"is_business_travel_ready\":[a-z]+,\"is_new_listing\":[a-z]+,\"lat\":[0-9]+.[0-9]+,\"lng\":-*[0-9]+.[0-9]+,\"name\":" %id_set_val_index,item)
                for longitude_note_one in long_note:
                    long_note_final = findall(",\"lng\":-*[0-9]+.[0-9]+,\"name\":", longitude_note_one) 
                    for long_list in long_note_final:
                        long = findall("-*\d+\.\d+", long_list)
                        for long_in in long:
                            #dat['ListingID'] = id_val
                            #dat['Long'] = long_in
                            #print long_in
                            a = long_in    
                for lat_list in lat_note:
                    lat_full = findall(",\"lat\":[0-9]+.[0-9]+,", lat_list)
                    for lat_values in lat_full:
                        lat = findall("\d+\.\d+", lat_values)
                      

                name_all = findall(",\"id\":%s,\"instant_bookable\":[a-z]+,\"is_business_travel_ready\":[a-z]+,\"is_new_listing\":[a-z]+,\"lat\":[0-9]+.[0-9]+,\"lng\":-*[0-9]+.[0-9]+,\"name\":(.*?),\"person_capacity\":" %id_set_val_index,item)
                #print("suspected error")          
                for name in name_all:
                    title_value_ex1 = findall(":(.*?),\"p", name) 
                    #print("suspected error") 
                    #print name               
                    title_name = name
                #user_id_first = findall("\"extra_host_languages\":\[.*?\],\"id\":%s,\"instant_bookable\":[a-z]+,\"is_business_travel_ready\":[a-z]+,\"is_new_listing\":[a-z]+,\"lat\":[0-9]+.[0-9]+,\"lng\":-*[0-9]+.[0-9]+,\"name\":(.*?),\"person_capacity\":[0-9]+,\"picture_count\":[0-9]+,\"picture_url\":(.*?),\"user\":{\"first_name\":[a-z]+,\"id\":[0-9]+" %id_set_val_index,item)
                user_id_first = findall("\"extra_host_languages\":\[.*?\],\"id\":%s,(.+?)nail_url\":" %id_set_val_index,item)
                #print user_id_first
                for users_index in user_id_first:
                    user_id = findall("\"id\":[0-9]+,\"thumb",users_index)
                    
                price_first = findall("\"extra_host_languages\":\[.*?\],\"id\":%s,(.+?)ency\":" %id_set_val_index,item)
                #print price_first
                for price_index in price_first:
                    price_id = findall("\"amount\":[0-9]+,\"curr",price_index)
                        
                dat = {}
                dat['Title'] = title_name 
                dat['UserID'] = user_id
                dat['Price'] = price_id
                dat['Lat'] = lat
                
                dat['ListingID'] = id_set_val_index
                #print dat['ListingID']
                dat['Long'] = a
                n+=1
                ListingDB.append(dat) 
            id_set.clear() 
            
        print n
        listings = tree.xpath('//div[@class="listing"]')
        
        content = tree.xpath('//div[@class="listing"]')
        
        return ListingDB

    except:
        print 'Error Parsing Page - Skipping: %s' % url
        #if there is an error, just return an empty list
        return ListingDB



#######################################
#  Detail Pages #######################
#######################################

def iterateDetail(mainResults):
    """
    This function takes the list of dictionaries returned by the
    IterateMainPage, and "enriches" the data with detailed data
    from the particular listing's info - if there is an error
    with getting that particular listing's info, the dictionary
    will be populated with default values of "Not Found"
    """
    finalResults = []
    counter = 0
    baseURL = 'https://www.airbnb.ca/rooms/'
    #for ll in mainResults:
        #print str(ll['ListingID'])
    for listing in mainResults:
        counter += 1
        #print 'Processing Listing %s out of %s' % (str(counter), str(len(mainResults)))
        #print str(listing['ListingID'])
        #Construct URL
        currentURL = ''.join([baseURL, str(listing['ListingID'])])
        #print currentURL
        #Get the tree
        tree = getTree(currentURL)

        #Parse the data out of the tree
        DetailResults = collectDetail(tree, listing['ListingID'])

        #Collect Data
        newListing = dict(listing.items() + DetailResults.items())

        #Append To Final Results
        finalResults.append(newListing)

    return finalResults


def fixDetail(mainResults, indexList):

    finalResults = mainResults[:]
    baseURL = 'https://www.airbnb.ca/rooms/'

    #redoList = [61, 62, 63, 64, 65, 66, 67, 443, 444, 445, 446, 447, 448, 449, \
    #450, 451, 452, 453, 454, 455, 456, 457, 458, 459]

    ######Only Modify This Part When You Want To Redo Certain Listings!!!###

    for i in indexList:
        #print 'fixing index %s' % str(i)
        listingID = str(finalResults[i]['ListingID'])
        currentURL = ''.join([baseURL, listingID])

        #Get the tree
        tree = getTree(currentURL)

        #Parse the data out of the tree
        DetailResults = collectDetail(tree, listingID)

        #Collect Data
        newListing = dict(finalResults[i].items() + DetailResults.items())

        #Append To Final Results
        finalResults[i] = newListing

    return finalResults


def getTree(url):
    """
    input
        url (string): this is a url string.  example: "http://www.google.com"

    output
        tree object:  will return a tree object if the url is found,
        otherwise will return a blank string
    """
    try:
        #Implement random time delay for scraping
        #sleep(randint(0,1))
        tree = html.fromstring(br.open(url).get_data())
        return tree

    except:
        #Pass An Empty String And Error Handling Of Children Functions Will Do
        #Appropriate Things
        #print 'Was not able to fetch data from %s' % url
        return ''


def collectDetail(treeObject, ListingID):
    Results = {'AboutListing': 'Not Found',
                     'HostName': 'Not Found',
                     'RespRate': 'Not Found',
                     'RespTime': 'Not Found',
                     'MemberDate': 'Not Found',
                     'R_acc' : 'Not Found',
                     'R_comm' : 'Not Found',
                     'R_clean' : 'Not Found',
                     'R_loc': 'Not Found',
                     'R_CI' : 'Not Found',
                     'R_val' : 'Not Found',
                     'P_ExtraPeople' : 'Not Found',
                     'P_Cleaning' : 'Not Found',
                     'P_Deposit' : 'Not Found',
                     'P_Weekly' : 'Not Found',
                     'P_Monthly' : 'Not Found',
                     'Cancellation' : 'Not Found',
                     'A_Kitchen' : 0,
                     'A_Internet' : 0,
                     'A_TV' : 0,
                     'A_Essentials' : 0,
                     'A_Shampoo' : 0,
                     'A_Heat' : 0,
                     'A_AC' : 0,
                     'A_Washer' : 0,
                     'A_Dryer' : 0,
                     'A_Parking' : 0,
                     'A_Internet' : 0,
                     'A_CableTV' : 0,
                     'A_Breakfast' :  0,
                     'A_Pets' : 0,
                     'A_FamilyFriendly' : 0,
                     'A_Events' : 0,
                     'A_Smoking' : 0,
                     'A_Wheelchair' : 0,
                     'A_Elevator' : 0,
                     'A_Fireplace' : 0,
                     'A_Intercom' : 0,
                     'A_Doorman' : 0,
                     'A_Pool' : 0,
                     'A_HotTub' : 0,
                     'A_Gym' : 0,
                     'A_SmokeDetector' : 0,
                     'A_CarbonMonoxDetector' : 0,
                     'A_FirstAidKit' : 0,
                     'A_SafetyCard' : 0,
                     'A_FireExt' : 0,
                     'S_PropType' : 'Not Found',
                     'S_Accomodates' : 'Not Found',
                     'S_Bedrooms' : 'Not Found',
                     'S_Bathrooms' : 'Not Found',
                     'S_NumBeds' : 'Not Found',
                     'S_BedType' : 'Not Found',
                     'S_CheckIn' : 'Not Found',
                     'S_Checkout' : 'Not Found'
                     }

    try:
       
        ###################
        
        Results['AboutListing'] = getAboutListing(treeObject, ListingID)
        Space = getSpaceInfo(treeObject, ListingID)
        Results['S_PropType'] = Space['PropType']
        Results['S_Accomodates'] = Space['Accommodates']
        Results['S_Bedrooms'] = Space['Bedrooms']
        Results['S_Bathrooms'] = Space['Bathrooms']
        Results['S_NumBeds'] = Space['NumBeds']
        Results['S_BedType'] = Space['BedType']
        Results['S_CheckIn'] = Space['CheckIn']
        Results['S_Checkout'] = Space['CheckOut']
       
        ####################
        Results['HostName'] = getHostName(treeObject, ListingID)
        Results['RespRate'], Results['RespTime'] = getHostResponse(TreeToSoup(treeObject), ListingID)
        Results['MemberDate'] = getMemberDate(TreeToSoup(treeObject), ListingID)

        #accuracy, communication, cleanliness, location, checkin, value
        Results['R_acc'], Results['R_comm'], Results['R_clean'], Results['R_loc'], \
        Results['R_CI'], Results['R_val'] = getStars(TreeToSoup(treeObject), ListingID)

        #price
        PriceData = getPriceInfo(treeObject, ListingID)
        Results['P_ExtraPeople'] = PriceData['ExtraPeople']
        Results['P_Cleaning'] = PriceData['CleaningFee']
        Results['P_Deposit'] = PriceData['SecurityDeposit']
        Results['P_Weekly'] = PriceData['WeeklyPrice']
        Results['P_Monthly'] = PriceData['MonthlyPrice']
        Results['Cancellation'] = PriceData['Cancellation']

        #Amenities
        Am = getAmenities(treeObject, ListingID)
        Results['A_Kitchen'] = Am['Kitchen']
        Results['A_Internet'] = Am['Internet']
        Results['A_TV'] = Am['TV']
        Results['A_Essentials'] = Am['Essentials' ]
        Results['A_Shampoo'] = Am['Shampoo']
        Results['A_Heat'] = Am['Heating']
        Results['A_AC'] = Am['Air Conditioning']
        Results['A_Washer'] = Am['Washer']
        Results['A_Dryer'] = Am['Dryer']
        Results['A_Parking'] = Am['Free Parking on Premises']
        Results['A_Internet'] = Am['Wireless Internet']
        Results['A_CableTV'] = Am['Cable TV' ]
        Results['A_Breakfast'] =  Am['Breakfast']
        Results['A_Pets'] = Am['Pets Allowed']
        Results['A_FamilyFriendly'] = Am['Family/Kid Friendly']
        Results['A_Events'] = Am['Suitable for Events']
        Results['A_Smoking'] = Am['Smoking Allowed']
        Results['A_Wheelchair'] = Am['Wheelchair Accessible']
        Results['A_Elevator'] = Am['Elevator in Building']
        Results['A_Fireplace'] = Am['Indoor Fireplace' ]
        Results['A_Intercom'] = Am['Buzzer/Wireless Intercom']
        Results['A_Doorman'] = Am['Doorman']
        Results['A_Pool'] = Am['Pool']
        Results['A_HotTub'] = Am['Hot Tub']
        Results['A_Gym'] = Am['Gym']
        Results['A_SmokeDetector'] = Am['Smoke Detector']
        Results['A_CarbonMonoxDetector'] = Am['Carbon Monoxide Detector']
        Results['A_FirstAidKit'] = Am['First Aid Kit' ]
        Results['A_SafetyCard'] = Am['Safety Card']
        Results['A_FireExt'] = Am['Fire Extinguisher']
        return Results

    except:
        #Just Return Initialized Dictionary
        return Results



def TreeToSoup(treeObject):
    """
    input: HTML element tree
    output: soup object (Beautiful Soup)
    This function converts an HTML element tree to a soup object
    """
    source = tostring(treeObject)
    soup = bs4.BeautifulSoup(source)
    return soup

################################################################
### Scrap the Host name Functions ##############################
################################################################

def getHostName(tree, ListingID):
   
    host_name = 'Not Found'

    try:
        host_name_path = tree.xpath('//h4[@class="row-space-2 text-center-sm"]')
        host_desc_iteration_path = tree.xpath('//div[@class="col-lg-8"]')
        for host_name_index in range(len(host_name_path)):
            host_name_parent = host_name_path[host_name_index]
            
            for desc in host_name_parent.iter():
                #print (desc.text)
                #print desc.xpath('@class')
                if(desc.text == 'Your Host'):
                        targetelement = host_name_parent.getnext().getnext().getparent()
                        break
                       
        #Depth - First Search of The Target Node
        host_name_descendants = targetelement.iterdescendants()    
        for host_descendant in host_name_descendants: 
            #check to make sure there is text in descendant
            if host_descendant.text:
                if ((host_descendant.text == " ") or (host_descendant.text == "Your Host")):
                    a = 1
                else:  
                    host_name = host_descendant.text
                    return host_name
            else:
                a = 1

    except:
        print 'Unable to parse host name for listing id: %s' % str(ListingID)
        return host_name

def getHostResponse(soup, ListingID):
  
    response_rate, response_time = ['Not Found'] * 2

    try:
        host_member = soup.find_all("div", {"class" : "col-md-6"})[-1]
        response_rate = host_member.find_all("strong")[0].text.encode('utf8')
        response_time = host_member.find_all("strong")[1].text.encode('utf8')
        return response_rate, response_time
        
    except:
        print 'Unable to parse response time for listing id: %s' % str(ListingID)
        return response_rate, response_time


def getMemberDate(soup, ListingID):
    
    membership_date = 'Not Found'

    try:
        host_member = soup.find_all("div", {"class" : "col-md-12 text-muted"})[0]
        membership_date = host_member.find_all("span")[-1].text.encode('utf8').strip("\n ")
        membership_date = membership_date.replace("Member since", "")
        return membership_date

    except:
        print 'Unable to parse membership date for listing id: %s' % str(ListingID)
        return membership_date


def singlestar(index, soup):
   
    stars = soup.find_all("div", {"class" : "foreground"})[index]
    full_star = stars.find_all("i", {"class" : "icon-star icon icon-light-gray icon-star-small"})
    half_star=  stars.find_all("i", {"class" : "icon-star icon icon-light-gray icon-star-half"})
    total_star = len(full_star)+len(half_star)*0.5
    return total_star


def getStars(soup, ListingID):
    
    accuracy, communication, cleanliness, location, checkin, value = ['Not Found'] * 6

    try:
        #accuracy starts at the third stars, right after the total reviews
        accuracy = singlestar(2, soup)
        communication = singlestar(3, soup)
        cleanliness = singlestar(4, soup)
        location = singlestar(5,soup)
        checkin = singlestar(6,soup)
        value = singlestar(7,soup)
        return accuracy, communication, cleanliness, location, checkin, value

    except:
        print 'Unable to parse stars listing id: %s' % str(ListingID)
        return accuracy, communication, cleanliness, location, checkin, value

##################################################
## Scraps the 'About Listing' description from the
## Airbnb listing page for the given City name and 
## Province name.
##################################################

def getAboutListing(tree, ListingID):
    """
    input: xmltree object
    output: string
    -----------------
    This function parses an individual listing's page to find
    the "About This Listing" and extracts the associated text
    """
    try:
    #Go To The Panel-Body
        elements = tree.xpath('//div[@class = "space-8 space-top-8"]/div/p/span/text()')
        return elements

    except:
        print 'Error finding *About Listing* for listing ID: %s' % ListingID
        return 'No Description Found'



def getSpaceInfo(tree, ListingID = 'Test'):

    """
    input: xmltree object
    output: dict
    -----------------
    This function parses an individual listing's page to find
    the all of the data in the "Space" row, such as Number of
    Bedrooms, Number of Bathrooms, Check In/Out Time, etc.
    """
    #Initialize Values
    dat = {'PropType': 'Not Found', 'Accommodates': 'Not Found',
           'Bedrooms': 'Not Found', 'Bathrooms' : 'Not Found',
           'NumBeds': 'Not Found', 'BedType': 'Not Found',
           'CheckIn': 'Not Found', 'CheckOut': 'Not Found'}
    
    global accommodate_switch 
    global propertytype_switch 
    global bathrooms_switch 
    global bedroom_switch 
    global checkin_switch 
    global beds_switch  
    global checkout_switch
    global bedtype_switch
    
    try:
        #Get Nodes That Contain The Grey Text, So That You Can Search For Sections
        
        #space_element_header = tree.xpath('//div[@class="row"]/div[@class="col-md-9"]/div[@class="row"]/div[@class="col-md-6"]/div/span/text()')
        #elements = tree.xpath('//div[@class="row"]/div[@class="col-md-9"]/div[@class="row"]/div[@class="col-md-6"]/div/strong/text()')
        
        sample = tree.xpath('//div[@class="row"]/div[@class="col-md-3 text-muted"]')
        
        for sample_index in range(len(sample)):
            parent = sample[sample_index]
            for desc in parent.iter():
                if(desc.text == 'The Space'):
                        targetelement = parent.getnext()
                        break
                       
        #Depth - First Search of The Target Node
        descendants = targetelement.iterdescendants()      
        
        for descendant in descendants: 
            #check to make sure there is text in descendant
            if descendant.text:
                
                if descendant.text == " ":
                    a = 1
                else:
                    
                    ##Find Property Type##
                    if descendant.text == 'Property type:':
                        propertytype_switch = True
                 
                    if ((propertytype_switch == True) and (descendant.tag == 'strong')):
                        propertytype_switch = False
                        dat['PropType'] = descendant.text   
                    
                    ##Find Accomodates ####
                    if descendant.text == 'Accommodates:':
                        accommodate_switch = True
                    
                    if ((accommodate_switch == True) and (descendant.tag == 'strong')):
                        accommodate_switch = False
                        dat['Accommodates'] = descendant.text
                        
                    ##Find Bedrooms ####
                    
                    if descendant.text =='Bedrooms:':
                        bedroom_switch = True
                
                    if ((bedroom_switch == True) and (descendant.tag == 'strong')):
                        bedroom_switch = False
                        dat['Bedrooms'] = descendant.text
                    
                    ##Find Bathrooms ####
                    if descendant.text =='Bathrooms:':
                        bathrooms_switch = True
                   
                
                    if ((bathrooms_switch == True) and (descendant.tag == 'strong')):
                        bathrooms_switch = False
                        dat['Bathrooms'] = descendant.text
                   
                    
                    ##Find Number of Beds ####
                    if descendant.text =='Beds:':
                        beds_switch = True
                   
                
                    if ((beds_switch == True) and (descendant.tag == 'strong')):
                        beds_switch = False
                        dat['NumBeds'] = descendant.text
                
                    
                    ##Find Bed Type ####
                    if descendant.text =='Bed type:':
                        bedtype_switch = True
                
               
                    if ((bedtype_switch == True) and (descendant.tag == 'strong')):
                        bedtype_switch = False
                        dat['BedType'] = descendant.text
             
                    
                    ##Find Check In Time ####
                    if descendant.text =='Check In:':
                        checkin_switch = True
                 
                
                    if ((checkin_switch == True) and (descendant.tag == 'strong')):
                        checkin_switch = False
                        dat['CheckIn'] = descendant.text  
               
            
                    ##Find Check Out Time ####
                    if descendant.text =='Check Out:':
                        checkout_switch = True
                
            
                    if ((checkout_switch == True) and (descendant.tag == 'strong')):
                        checkout_switch = False
                        dat['CheckOut'] = descendant.text
            
            
            else:
                        a = 1    
            
        accommodate_switch = False
        propertytype_switch = False
        bathrooms_switch = False
        bedroom_switch = False
        checkin_switch = False
        beds_switch  = False
        checkout_switch = False
        bedtype_switch = False
        return dat
         
    except:
        print 'Error in getting Space Elements for listing ID: %s' % str(ListingID)
        print "Unexpected error:", sys.exc_info()[0]
        return dat

#######################################
#  Price Functions #####################
#######################################

def getPriceInfo(tree, ListingID):
    """
    input: xmltree object
    output: dict
    -----------------
    This function parses an individual listing's page to find
    the all of the data in the "Price" row, such as Cleaning Fee, Security Deposit, Weekly Price, etc.
    """
    #Initialize Values
    dat = {'ExtraPeople': 'Not Found', 'CleaningFee': 'Not Found', 'SecurityDeposit': 'Not Found',
       'WeeklyPrice': 'Not Found','MonthlyPrice': 'Not Found','Cancellation' : 'Not Found'}
    
    global extrapeople_switch 
    global cleaningfee_switch 
    global securitydeposit_switch 
    global weeklyprice_switch 
    global monthlyprice_switch 
    global cancellation_switch  
    
    
    try:
        #Get Nodes That Contain The Grey Text, So That You Can Search For Sections
        elements = tree.xpath('//div[@class="row"]/div[@class="col-md-3 text-muted"]')

        #find The price portion of the page,
        #then go back up one level and sideways one level
        for elements_index in range(len(elements)):
            parent = elements[elements_index]
            for desc in parent.iter():
                #print (desc.text)
                #print desc.xpath('@class')
                if(desc.text == 'Prices'):
                        targetelement = parent.getnext()
                        break

        #Depth - First Search of The Target Node
        descendants = targetelement.iterdescendants()
        
        for descendant in descendants: 
            #check to make sure there is text in descendant
            if descendant.text:
                
                if " " in descendant.text:
                    a = 1
                else:
                    ##Find Property Type##
                    if descendant.text == 'Extra people:':
                        #print("property type")
                        extrapeople_switch = True
                 
                    if ((extrapeople_switch == True) and (descendant.tag == 'strong')):
                        extrapeople_switch = False
                        dat['ExtraPeople'] = descendant.text   
                    
                    ##Find Accomodates ####
                    if descendant.text == 'Cleaning Fee:':
                        cleaningfee_switch = True
                    
                    if ((cleaningfee_switch == True) and (descendant.tag == 'strong')):
                        cleaningfee_switch = False
                        dat['CleaningFee'] = descendant.text
                        
                    ##Find Bedrooms ####
                    
                    if descendant.text =='Security Deposit:':
                        securitydeposit_switch = True
                
                    if ((securitydeposit_switch == True) and (descendant.tag == 'strong')):
                        securitydeposit_switch = False
                        dat['SecurityDeposit'] = descendant.text
                    
                    ##Find Bathrooms ####
                    if descendant.text =='Weekly Price:':
                        weeklyprice_switch = True
                   
                
                    if ((weeklyprice_switch == True) and (descendant.tag == 'strong')):
                        weeklyprice_switch = False
                        dat['WeeklyPrice'] = descendant.text
                   

                    ##Find Number of Beds ####
                    if descendant.text =='Monthly Price:':
                        monthlyprice_switch = True
                   
                
                    if ((monthlyprice_switch == True) and (descendant.tag == 'strong')):
                        monthlyprice_switch = False
                        dat['MonthlyPrice'] = descendant.text
                
            
                    ##Find Bed Type ####
                    if descendant.text =='Cancellation:':
                        cancellation_switch = True
                
               
                    if ((cancellation_switch == True) and (descendant.tag == 'strong')):
                        cancellation_switch = False
                        dat['Cancellation'] = descendant.text
            else:
                        a = 1    
            
        extrapeople_switch = False
        cleaningfee_switch = False
        securitydeposit_switch = False
        weeklyprice_switch = False
        monthlyprice_switch = False
        cancellation_switch  = False
        return dat

    except:
        print 'Error in getting Price Elements for listing iD: %s' % str(ListingID)
        return dat

#########################################
#  Amenities ############################
#########################################
def getAmenitiesList(tree, ListingID):
    """
    input: xmltree object
    output: list of available amenities
    -----------------
    This function parses an individual listing's page to find
    the amenities available in the listing.  The amenities that are available
    are collected into a list.
    """
    amenities = []

    try:
        #Get Nodes That Contain The Grey Text, So That You Can Search For Sections
        elements = tree.xpath('//div[@class="row amenities"]/div[@class="col-md-3 text-muted"]')

        #find The price portion of the page,
        #then go back up one level and sideways one level
        
        for elements_index in range(len(elements)):
            parent = elements[elements_index]
            for desc in parent.iter():
                if(desc.text == 'Amenities'):
                        targetelement = parent.getnext()
                        break

        #Depth - First Search of The Target Node
        descendants = targetelement.iterdescendants()
        
        for descendant in descendants: 
            #check to make sure there is text in descendant
            if descendant.text:
                
                if " " in descendant.text:
                    a = 1
                else:
                    amenities.append(descendant.text)
                    
            else:
                a = 1   
            
        
        return list(set(amenities))

    except:
        print 'Error in getting amenities for listing iD: %s' % str(ListingID)
        return amenities


def getAmenities(tree, ListingID):
    """
    input: xmltree object
    output: dict of binary indication if amenity exists or not
    -----------------
    This function parses an individual listing's page to find
    the amenities available in the listing.  The amenities that are available
    are collected into a list.
    """

    #Initialize Values
    dat = {'Kitchen': 0, 'Internet': 0, 'TV': 0, 'Essentials' : 0,
           'Shampoo': 0, 'Heating': 0, 'Air Conditioning': 0, 'Washer': 0,
           'Dryer': 0, 'Free Parking on Premises': 0,
           'Wireless Internet': 0, 'Cable TV' : 0,'Breakfast': 0, 'Pets Allowed': 0,
           'Family/Kid Friendly': 0, 'Suitable for Events': 0,
           'Smoking Allowed': 0, 'Wheelchair Accessible': 0,
           'Elevator in Building': 0, 'Indoor Fireplace' : 0,
           'Buzzer/Wireless Intercom': 0, 'Doorman': 0,
           'Pool': 0, 'Hot Tub': 0, 'Gym': 0,'Smoke Detector': 0,
           'Carbon Monoxide Detector': 0, 'First Aid Kit' : 0,
           'Safety Card': 0, 'Fire Extinguisher': 0}

    amenities = getAmenitiesList(tree, ListingID)

    for amenity in dat.keys():
        if amenity in amenities:
            dat[amenity] = 1

    return dat

######################################
#### Save Results ####################

class DictUnicodeWriter(object):

    def __init__(self, f, fieldnames, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.DictWriter(self.queue, fieldnames, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, D):
        self.writer.writerow({k:v.encode("utf-8") if isinstance(v, unicode) else v for k,v in D.items()})
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for D in rows:
            self.writerow(D)

    def writeheader(self):
        self.writer.writeheader()

def writeToCSV(resultDict, outfile):

    colnames = [ 'ListingID', 'Title','UserID','baseurl',  'Price', \
        'AboutListing','HostName', 'MemberDate', 'Lat','Long','BookInstantly','Cancellation',  \
        'OverallCounter','PageCounter','PageNumber', \
         'A_AC','A_Breakfast','A_CableTV','A_CarbonMonoxDetector','A_Doorman','A_Dryer','A_TV', \
         'A_Elevator','A_Essentials','A_Events','A_FamilyFriendly','A_FireExt','A_Fireplace','A_FirstAidKit', \
         'A_Gym','A_Heat','A_HotTub','A_Intercom','A_Internet','A_Kitchen','A_Parking','A_Pets','A_Pool','A_SafetyCard', \
         'A_Shampoo','A_SmokeDetector','A_Smoking','A_Washer','A_Wheelchair', \
         'P_Cleaning','P_Deposit','P_ExtraPeople','P_Monthly','P_Weekly', \
         'R_CI','R_acc','R_clean','R_comm', \
         'R_loc','R_val', \
         'RespRate','RespTime', \
         'S_Accomodates','S_Bathrooms','S_BedType','S_Bedrooms', \
         'S_CheckIn','S_Checkout','S_NumBeds','S_PropType','ShortDesc']

    with open(outfile, 'wb') as f:
        w = DictUnicodeWriter(f, fieldnames=colnames)
        w.writeheader()
        w.writerows(resultDict)

##############################################
#######Getting the user argument from the User
##############################################
def init_parser():
    
    parser = argparse.ArgumentParser(description="Please give the place name in the format, city--Provincename"
    )
     
    # Positional arguments
    
    parser.add_argument('placename', action='store',
        help='This this the path of the given directory where all the documents resides in in UTF-8 fromat')
     
    parser.add_argument('num_of_pages', action='store',
        help='This this the path of the given directory where all the documents resides in in UTF-8 fromat')
    return parser.parse_args()



#######################################
#  Main function#######################
#######################################

if __name__ == '__main__':
    
    
    parser = init_parser()
    placename = parser.placename.split(',')
    num_of_pages = parser.num_of_pages
    for i in placename:
        
        accommodate_switch = False
        propertytype_switch = False
        bathrooms_switch = False
        bedroom_switch = False
        checkin_switch = False
        beds_switch  = False
        checkout_switch = False
        bedtype_switch = False
        extrapeople_switch = False
        cleaningfee_switch = False
        securitydeposit_switch = False
        weeklyprice_switch = False
        monthlyprice_switch = False
        cancellation_switch  = False
    
        #Iterate Through Main Page To Get Results
        MainResults = IterateMainPage(i,num_of_pages)

        #Take The Main Results From Previous Step and Iterate Through Each Listing
        #To add more detail
        DetailResults = iterateDetail(MainResults)
        today_date = time.strftime("%d-%m-%Y")
        output_file_name = 'OutputFile' + '_' + i + '_' + today_date + '.txt'
        #Write Out Results To CSV File, using function I defined
        writeToCSV(DetailResults, output_file_name)
        

