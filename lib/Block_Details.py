import json
from decimal import Decimal

from flask import Flask, render_template, request, jsonify, session, redirect, escape, url_for

#class ServerError(Exception)
import sys

class Block:
    def __init__ (self, bid,bname, pincode, hid):# maxlat, maxlong, minlat, minLong):
         self.bid = bid
         self.bname = bname
         self.pincode = pincode
         self.hid = hid
         #self.mexlat = maxlat
         #self.maxlong = maxlong
         #self.minlat = minlat
         #self.minLong = minLong

def getblock_info(db):
    error = None
    try:
        blocklist = []
        cur = db.query("SELECT bid,bname,block_Image,pincode,hid FROM block_details")

        #blocklist = [Block() for i in cur.fetchall()]

        for bid, bname, block_Image, pincode, hid in cur.fetchall():
            bid = bid
            bname = bname
            bimg = block_Image
            pincode = pincode
            hid = hid
            """
            maxlat = row['maxlat']
            maxlong = row['maxlong']
            minlat = row['minlat']
            minlong = row['minlong']
            """
            #b = Block(bid, bname, pincode, hid, maxlat, maxlong, minlat, minlong)
            blocklist.append({'bid': bid, 'bname': bname, 'bimg': bimg,
                              'pincode': pincode, 'hid': hid})
                                #'maxlat': maxlat,
                              #'maxlong': maxlong, 'minlat': minlat, 'minlong': minlong})


        return blocklist
    except IOError as err:
        print("I/O error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")
    except:
        print("Unexpected error:", sys.exc_info()[0])
        error = "Failed"
        return error

def joinBlock_Request(db, blockId):
    error = None
    try:
        print('Username active :', session['username'])
        print('Block Id :', blockId)

    except IOError as err:
        print("I/O error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")
    except:
        print("Unexpected error:", sys.exc_info()[0])
        error = "Failed"
        return error
