from osint_stringUtils import stringBetween
import math

class NaiveURLParsing_ExcludePatter:
  def __init__(self, start, end):
    self.start = start
    self.end = end

def naiveURLParsing(URL, possibleNetlocs, memberExcludePatterns):

  isTargetURL = False
  
  for possibleNetloc in possibleNetlocs:
    if possibleNetloc in URL:
      isTargetURL = True
      break
  
  if not isTargetURL:
    return None
  
  members = []

  for memberExcludePattern in memberExcludePatterns:
  
    startPatterns = memberExcludePattern.start
    endPatterns = memberExcludePattern.end
  
    member = None
    for startPattern in startPatterns:
      
      for endPattern in endPatterns:
        possibleMember = stringBetween(URL, startPattern, endPattern)
        
        if possibleMember != None:
          if member == None or len(member) > len(possibleMember):
            member = possibleMember
     
    members.append(member)
  
  return members

#============================== YouTube ==============================

class YouTubeURLInfo:
  def __init__(self, videoID):
    self.videoID = videoID

def tryParseYouTube(URL):
  
  # Parsing is based on list of possible YouTube URL formats: 
  # [https://gist.github.com/rodrigoborgesdeoliveira/987683cfbfcc8d800192da1e73adc486]
  #
  # NOTE: Currently not all formats are supported!
  
  # Currently perform very simple and naive parsing:
  # 1. Check if URL contains 
  # 2. Exclude members by 
  #
  # May work incorrect case like:
  #
  # www.someCuriousSite.com/parse?urls="www.youtube.com,youtube.com"
  # ---------------------------------------------------------------------
  
  #For checking if URL is even youtube URL
 
  possibleNetlocs = [\
    "www.youtube.com",\
    "youtube.com",\
    "m.youtube.com",\
    "youtu.be",
    "www.youtube-nocookie.com"\
  ]
  
  #For excluding video ID
  
  excludePattern_videoID_start = [\
    "v=",\
    "vi=",\
    "v/",\
    "a=",\
    "e/",\
    "youtu.be/",\
    "shorts/",\
    "embed/",
    "?v%3D"\
  ]
  
  excludePattern_videoID_end = [\
    "&",\
    "?",
    "#",\
    None\
  ]
  
  #Perform parsing and return result
  
  members = naiveURLParsing(URL, possibleNetlocs, [\
    NaiveURLParsing_ExcludePatter(excludePattern_videoID_start, excludePattern_videoID_end)\
  ])

  if members == None:
    return None
    
  return YouTubeURLInfo(members[0])


#=========================== Google Drive ===========================

class GoogleDriveURLInfo:
  def __init__(self, itemID):
    self.itemID = itemID

#https://drive.google.com/file/d/1LxGG6gK-pikxvdNiZyvxnUr2NVoKqglG/view?usp=drive_link

def tryParseGoogleDriveURL(URL):

  #For checking if URL is even youtube URL

  possibleNetlocs = [\
    "docs.google.com",\
    "script.google.com",\
    "drive.google.com"
  ]
  
  #For excluding video ID
  
  excludePattern_ID_start = [\
    "d/"\
  ]
  
  excludePattern_ID_end = [\
    "/view",\
    "/edit",\
    None\
  ]
  
  #Perform parsing and return result
  
  members = naiveURLParsing(URL, possibleNetlocs, [\
    NaiveURLParsing_ExcludePatter(excludePattern_ID_start, excludePattern_ID_end)\
  ])

  if members == None:
    return None
    
  return GoogleDriveURLInfo(members[0]) 

#===================== Timestamped URL ========================

def tryMakeTimestampedURL(URL, time):
  
  possibleYouTubeURLInfo = tryParseYouTube(URL)
  if possibleYouTubeURLInfo != None:
    return "https://www.youtube.com/watch?v={videoID}&t={seconds}".format(\
      videoID = possibleYouTubeURLInfo.videoID,
      seconds = math.floor(time.total_seconds()))

  possibleGoogleDriveURLInfo = tryParseGoogleDriveURL(URL)
  if possibleGoogleDriveURLInfo != None: 
    return "https://drive.google.com/file/d/{itemID}/view?t={seconds}".format(\
      itemID = possibleGoogleDriveURLInfo.itemID,
      seconds = math.floor(time.total_seconds()))

  return URL


#=========================== Test ===========================

def runURLParsingTest():

  testYouTubeURLs = [\
    "http://www.youtube.com/watch?v=-wtIMTCHWuI",\
    "http://youtube.com/watch?v=-wtIMTCHWuI",\
    "http://m.youtube.com/watch?v=-wtIMTCHWuI",\
    "https://www.youtube.com/watch?v=lalOy8Mbfdc",\
    "https://youtube.com/watch?v=lalOy8Mbfdc",\
    "https://m.youtube.com/watch?v=lalOy8Mbfdc",\
    "http://www.youtube.com/watch?v=yZv2daTWRZU&feature=em-uploademail",\
    "http://youtube.com/watch?v=yZv2daTWRZU&feature=em-uploademail",\
    "http://m.youtube.com/watch?v=yZv2daTWRZU&feature=em-uploademail",\
    "https://www.youtube.com/watch?v=yZv2daTWRZU&feature=em-uploademail",\
    "https://youtube.com/watch?v=yZv2daTWRZU&feature=em-uploademail",\
    "https://m.youtube.com/watch?v=yZv2daTWRZU&feature=em-uploademail",\
    "http://www.youtube.com/watch?v=0zM3nApSvMg&feature=feedrec_grec_index",\
    "http://youtube.com/watch?v=0zM3nApSvMg&feature=feedrec_grec_index",\
    "http://m.youtube.com/watch?v=0zM3nApSvMg&feature=feedrec_grec_index",\
    "https://www.youtube.com/watch?v=0zM3nApSvMg&feature=feedrec_grec_index",\
    "https://youtube.com/watch?v=0zM3nApSvMg&feature=feedrec_grec_index",\
    "https://m.youtube.com/watch?v=0zM3nApSvMg&feature=feedrec_grec_index",\
    "http://www.youtube.com/watch?v=0zM3nApSvMg#t=0m10s",\
    "http://youtube.com/watch?v=0zM3nApSvMg#t=0m10s",\
    "http://m.youtube.com/watch?v=0zM3nApSvMg#t=0m10s",\
    "https://www.youtube.com/watch?v=0zM3nApSvMg#t=0m10s",\
    "https://youtube.com/watch?v=0zM3nApSvMg#t=0m10s",\
    "https://m.youtube.com/watch?v=0zM3nApSvMg#t=0m10s",\
    "http://www.youtube.com/watch?v=cKZDdG9FTKY&feature=channel",\
    "http://youtube.com/watch?v=cKZDdG9FTKY&feature=channel",\
    "http://m.youtube.com/watch?v=cKZDdG9FTKY&feature=channel",\
    "https://www.youtube.com/watch?v=oTJRivZTMLs&feature=channel",\
    "https://youtube.com/watch?v=oTJRivZTMLs&feature=channel",\
    "https://m.youtube.com/watch?v=oTJRivZTMLs&feature=channel",\
    "http://www.youtube.com/watch?v=lalOy8Mbfdc&playnext_from=TL&videos=osPknwzXEas&feature=sub",\
    "http://youtube.com/watch?v=lalOy8Mbfdc&playnext_from=TL&videos=osPknwzXEas&feature=sub",\
    "http://m.youtube.com/watch?v=lalOy8Mbfdc&playnext_from=TL&videos=osPknwzXEas&feature=sub",\
    "https://www.youtube.com/watch?v=lalOy8Mbfdc&playnext_from=TL&videos=osPknwzXEas&feature=sub",\
    "https://youtube.com/watch?v=lalOy8Mbfdc&playnext_from=TL&videos=osPknwzXEas&feature=sub",\
    "https://m.youtube.com/watch?v=lalOy8Mbfdc&playnext_from=TL&videos=osPknwzXEas&feature=sub",\
    "http://www.youtube.com/watch?v=lalOy8Mbfdc&feature=youtu.be",\
    "http://youtube.com/watch?v=lalOy8Mbfdc&feature=youtu.be",\
    "http://m.youtube.com/watch?v=lalOy8Mbfdc&feature=youtu.be",\
    "https://www.youtube.com/watch?v=lalOy8Mbfdc&feature=youtu.be",\
    "https://youtube.com/watch?v=lalOy8Mbfdc&feature=youtu.be",\
    "https://m.youtube.com/watch?v=lalOy8Mbfdc&feature=youtu.be",\
    "http://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=youtube_gdata_player",\
    "http://youtube.com/watch?v=dQw4w9WgXcQ&feature=youtube_gdata_player",\
    "http://m.youtube.com/watch?v=dQw4w9WgXcQ&feature=youtube_gdata_player",\
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=youtube_gdata_player",\
    "https://youtube.com/watch?v=dQw4w9WgXcQ&feature=youtube_gdata_player",\
    "https://m.youtube.com/watch?v=dQw4w9WgXcQ&feature=youtube_gdata_player",\
    "http://www.youtube.com/watch?v=ishbTyLs6ps&list=PLGup6kBfcU7Le5laEaCLgTKtlDcxMqGxZ&index=106&shuffle=2655",\
    "http://youtube.com/watch?v=ishbTyLs6ps&list=PLGup6kBfcU7Le5laEaCLgTKtlDcxMqGxZ&index=106&shuffle=2655",\
    "http://m.youtube.com/watch?v=ishbTyLs6ps&list=PLGup6kBfcU7Le5laEaCLgTKtlDcxMqGxZ&index=106&shuffle=2655",\
    "https://www.youtube.com/watch?v=ishbTyLs6ps&list=PLGup6kBfcU7Le5laEaCLgTKtlDcxMqGxZ&index=106&shuffle=2655",\
    "https://youtube.com/watch?v=ishbTyLs6ps&list=PLGup6kBfcU7Le5laEaCLgTKtlDcxMqGxZ&index=106&shuffle=2655",\
    "https://m.youtube.com/watch?v=ishbTyLs6ps&list=PLGup6kBfcU7Le5laEaCLgTKtlDcxMqGxZ&index=106&shuffle=2655",\
    "http://www.youtube.com/watch?feature=player_embedded&v=dQw4w9WgXcQ",\
    "http://youtube.com/watch?feature=player_embedded&v=dQw4w9WgXcQ",\
    "http://m.youtube.com/watch?feature=player_embedded&v=dQw4w9WgXcQ",\
    "https://www.youtube.com/watch?feature=player_embedded&v=dQw4w9WgXcQ",\
    "https://youtube.com/watch?feature=player_embedded&v=dQw4w9WgXcQ",\
    "https://m.youtube.com/watch?feature=player_embedded&v=dQw4w9WgXcQ",\
    "http://www.youtube.com/watch?app=desktop&v=dQw4w9WgXcQ",\
    "http://youtube.com/watch?app=desktop&v=dQw4w9WgXcQ",\
    "http://m.youtube.com/watch?app=desktop&v=dQw4w9WgXcQ",\
    "https://www.youtube.com/watch?app=desktop&v=dQw4w9WgXcQ",\
    "https://youtube.com/watch?app=desktop&v=dQw4w9WgXcQ",\
    "https://m.youtube.com/watch?app=desktop&v=dQw4w9WgXcQ",\
    "http://www.youtube.com/v/dQw4w9WgXcQ",\
    "http://youtube.com/v/dQw4w9WgXcQ",\
    "http://m.youtube.com/v/dQw4w9WgXcQ",\
    "https://www.youtube.com/v/dQw4w9WgXcQ",\
    "https://youtube.com/v/dQw4w9WgXcQ",\
    "https://m.youtube.com/v/dQw4w9WgXcQ",\
    "http://www.youtube.com/v/-wtIMTCHWuI?version=3&autohide=1",\
    "http://youtube.com/v/-wtIMTCHWuI?version=3&autohide=1",\
    "http://m.youtube.com/v/-wtIMTCHWuI?version=3&autohide=1",\
    "https://www.youtube.com/v/-wtIMTCHWuI?version=3&autohide=1",\
    "https://youtube.com/v/-wtIMTCHWuI?version=3&autohide=1",\
    "https://m.youtube.com/v/-wtIMTCHWuI?version=3&autohide=1",\
    "http://www.youtube.com/v/0zM3nApSvMg?fs=1&hl=en_US&rel=0",\
    "http://youtube.com/v/0zM3nApSvMg?fs=1&hl=en_US&rel=0",\
    "http://m.youtube.com/v/0zM3nApSvMg?fs=1&hl=en_US&rel=0",\
    "https://www.youtube.com/v/0zM3nApSvMg?fs=1&amp;hl=en_US&amp;rel=0",\
    "https://www.youtube.com/v/0zM3nApSvMg?fs=1&hl=en_US&rel=0",\
    "https://youtube.com/v/0zM3nApSvMg?fs=1&hl=en_US&rel=0",\
    "https://m.youtube.com/v/0zM3nApSvMg?fs=1&hl=en_US&rel=0",\
    "http://www.youtube.com/v/dQw4w9WgXcQ?feature=youtube_gdata_player",\
    "http://youtube.com/v/dQw4w9WgXcQ?feature=youtube_gdata_player",\
    "http://m.youtube.com/v/dQw4w9WgXcQ?feature=youtube_gdata_player",\
    "https://www.youtube.com/v/dQw4w9WgXcQ?feature=youtube_gdata_player",\
    "https://youtube.com/v/dQw4w9WgXcQ?feature=youtube_gdata_player",\
    "https://m.youtube.com/v/dQw4w9WgXcQ?feature=youtube_gdata_player",\
    "http://youtu.be/-wtIMTCHWuI",\
    "https://youtu.be/-wtIMTCHWuI",\
    "http://youtu.be/dQw4w9WgXcQ?feature=youtube_gdata_player",\
    "https://youtu.be/dQw4w9WgXcQ?feature=youtube_gdata_player",\
    "http://youtu.be/oTJRivZTMLs?list=PLToa5JuFMsXTNkrLJbRlB--76IAOjRM9b",\
    "https://youtu.be/oTJRivZTMLs?list=PLToa5JuFMsXTNkrLJbRlB--76IAOjRM9b",\
    "http://youtu.be/oTJRivZTMLs&feature=channel",\
    "https://youtu.be/oTJRivZTMLs&feature=channel",\
    "http://youtu.be/lalOy8Mbfdc?t=1",\
    "http://youtu.be/lalOy8Mbfdc?t=1s",\
    "https://youtu.be/lalOy8Mbfdc?t=1",\
    "https://youtu.be/lalOy8Mbfdc?t=1s",\
    "http://www.youtube.com/oembed?url=http%3A//www.youtube.com/watch?v%3D-wtIMTCHWuI&format=json",\
    "http://youtube.com/oembed?url=http%3A//www.youtube.com/watch?v%3D-wtIMTCHWuI&format=json",\
    "http://m.youtube.com/oembed?url=http%3A//www.youtube.com/watch?v%3D-wtIMTCHWuI&format=json",\
    "https://www.youtube.com/oembed?url=http%3A//www.youtube.com/watch?v%3D-wtIMTCHWuI&format=json",\
    "https://youtube.com/oembed?url=http%3A//www.youtube.com/watch?v%3D-wtIMTCHWuI&format=json",\
    "https://m.youtube.com/oembed?url=http%3A//www.youtube.com/watch?v%3D-wtIMTCHWuI&format=json",\
    "http://www.youtube.com/attribution_link?a=JdfC0C9V6ZI&u=%2Fwatch%3Fv%3DEhxJLojIE_o%26feature%3Dshare",\
    "http://youtube.com/attribution_link?a=JdfC0C9V6ZI&u=%2Fwatch%3Fv%3DEhxJLojIE_o%26feature%3Dshare",\
    "http://m.youtube.com/attribution_link?a=JdfC0C9V6ZI&u=%2Fwatch%3Fv%3DEhxJLojIE_o%26feature%3Dshare",\
    "https://www.youtube.com/attribution_link?a=JdfC0C9V6ZI&u=%2Fwatch%3Fv%3DEhxJLojIE_o%26feature%3Dshare",\
    "https://youtube.com/attribution_link?a=JdfC0C9V6ZI&u=%2Fwatch%3Fv%3DEhxJLojIE_o%26feature%3Dshare",\
    "https://m.youtube.com/attribution_link?a=JdfC0C9V6ZI&u=%2Fwatch%3Fv%3DEhxJLojIE_o%26feature%3Dshare",\
    "http://www.youtube.com/attribution_link?a=8g8kPrPIi-ecwIsS&u=/watch%3Fv%3DyZv2daTWRZU%26feature%3Dem-uploademail",\
    "http://youtube.com/attribution_link?a=8g8kPrPIi-ecwIsS&u=/watch%3Fv%3DyZv2daTWRZU%26feature%3Dem-uploademail",\
    "http://m.youtube.com/attribution_link?a=8g8kPrPIi-ecwIsS&u=/watch%3Fv%3DyZv2daTWRZU%26feature%3Dem-uploademail",\
    "https://www.youtube.com/attribution_link?a=8g8kPrPIi-ecwIsS&u=/watch%3Fv%3DyZv2daTWRZU%26feature%3Dem-uploademail",\
    "https://youtube.com/attribution_link?a=8g8kPrPIi-ecwIsS&u=/watch%3Fv%3DyZv2daTWRZU%26feature%3Dem-uploademail",\
    "https://m.youtube.com/attribution_link?a=8g8kPrPIi-ecwIsS&u=/watch%3Fv%3DyZv2daTWRZU%26feature%3Dem-uploademail",\
    "http://www.youtube.com/embed/lalOy8Mbfdc",\
    "http://youtube.com/embed/lalOy8Mbfdc",\
    "http://m.youtube.com/embed/lalOy8Mbfdc",\
    "https://www.youtube.com/embed/lalOy8Mbfdc",\
    "https://youtube.com/embed/lalOy8Mbfdc",\
    "https://m.youtube.com/embed/lalOy8Mbfdc",\
    "http://www.youtube.com/embed/nas1rJpm7wY?rel=0",\
    "http://youtube.com/embed/nas1rJpm7wY?rel=0",\
    "http://m.youtube.com/embed/nas1rJpm7wY?rel=0",\
    "https://www.youtube.com/embed/nas1rJpm7wY?rel=0",\
    "https://youtube.com/embed/nas1rJpm7wY?rel=0",\
    "https://m.youtube.com/embed/nas1rJpm7wY?rel=0",\
    "http://www.youtube-nocookie.com/embed/lalOy8Mbfdc?rel=0",\
    "https://www.youtube-nocookie.com/embed/lalOy8Mbfdc?rel=0",\
    "http://www.youtube.com/e/dQw4w9WgXcQ",\
    "http://youtube.com/e/dQw4w9WgXcQ",\
    "http://m.youtube.com/e/dQw4w9WgXcQ",\
    "https://www.youtube.com/e/dQw4w9WgXcQ",\
    "https://youtube.com/e/dQw4w9WgXcQ",\
    "https://m.youtube.com/e/dQw4w9WgXcQ",\
    "https://youtube.com/user/GitHub#p/a/u/1/lalOy8Mbfdc",\
    "https://www.youtube.com/user/GitHub#p/u/1/lalOy8Mbfdc",\
    "https://www.youtube.com/user/GitHub#p/u/1/lalOy8Mbfdc?rel=0",\
    "https://www.youtube.com/user/GitHub#p/a/u/2/lalOy8Mbfdc",\
    "https://www.youtube.com/user/GitHub#p/u/11/lalOy8Mbfdc",\
    "https://www.youtube.com/user/GitHub#p/u/1/lalOy8Mbfdc",\
    "https://www.youtube.com/GitHub?v=lalOy8Mbfdc",\
    "http://www.youtube.com/?v=dQw4w9WgXcQ",\
    "http://youtube.com/?v=dQw4w9WgXcQ&feature=youtube_gdata_player",\
    "http://youtube.com/?v=lalOy8Mbfdc&feature=channel",\
    "http://youtube.com/?vi=dQw4w9WgXcQ",\
    "http://youtube.com/?vi=dQw4w9WgXcQ&feature=youtube_gdata_player",\
    "http://youtube.com/?vi=lalOy8Mbfdc&feature=channel",\
    "http://www.youtube.com/?feature=player_embedded&v=dQw4w9WgXcQ",\
    "http://youtube.com/?feature=channel&v=lalOy8Mbfdc",\
    "http://youtube.com/watch?vi=dQw4w9WgXcQ",\
    "http://youtube.com/watch?vi=dQw4w9WgXcQ&feature=youtube_gdata_player",\
    "http://youtube.com/watch?vi=lalOy8Mbfdc&feature=channel",\
    "http://youtube.com/vi/dQw4w9WgXcQ",\
    "http://youtube.com/vi/dQw4w9WgXcQ?feature=youtube_gdata_player",\
    "http://youtube.com/vi/lalOy8Mbfdc&feature=channel",\
    "http://www.youtube-nocookie.com/v/6L3ZvIMwZFM?version=3&hl=en_US&rel=0",\
  ]
  
  print(" =============================================== ")
  
  for testYouTubeURL in testYouTubeURLs:
  
    URLInfo = tryParseYouTube(testYouTubeURL)
    
    print("- - - - - -")
    print(testYouTubeURL)
    
    if URLInfo != None:
      print(URLInfo.videoID)
    else:
      print("Unsuccess parse")
  
  # ====================================================
  # Google drive
  
  testGoogleDriveURLs = [\
    "https://docs.google.com/document/d/1GefQPC9bkTSP1AzZr7E90k8tgctSeV2su7xFWlLScEA/edit?usp=drive_link",\
    "https://docs.google.com/spreadsheets/d/1GQLgULKA3O8CeFcKkaDPZTocrbS8wyqNZ5lMSVT6q0s/edit?usp=drive_link",\
    "https://docs.google.com/presentation/d/1IHMxmu31ne64kLcO-svGNyHC1wB4LeKija292T24GHY/edit?usp=drive_link",\
    "https://script.google.com/d/1Xr91DqL9ijnrARWrazT5RDQPB5JmjJh8t-zL2nJnvOCm2V2AdhkOvaYq/edit?usp=drive_link",\
    "https://drive.google.com/file/d/1LxGG6gK-pikxvdNiZyvxnUr2NVoKqglG/view?t=5", \
    "https://drive.google.com/file/d/1-6Bja8xpVRVO-GpNBygyPq6anxpEoIGl/view?usp=drive_link"
  ]
  
  # Last two URLS:
  # first - video, support time access
  # second - not video, don't support time access
  
  for testGoogleDriveURL in testGoogleDriveURLs:
  
    URLInfo = tryParseGoogleDriveURL(testGoogleDriveURL)
    
    print("- - - - - -")
    print(testGoogleDriveURL)
    
    if URLInfo != None:
      print(URLInfo.itemID)
    else:
      print("Unsuccess parse")
