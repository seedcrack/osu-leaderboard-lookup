from ossapi import Ossapi
import pandas as pd
pd.set_option('display.max_rows', 100)

def API_Validity(client_ID,client_secret): #check if the API is valid
    try:
        api = Ossapi(client_ID,client_secret)
        return "Valid"
    except:
        return "This client ID / client secret is invalid, please try again"
    
def FAQ(): #in case any prof wants to know what osu! is
    print("Hello this is the FAQ, what questions do you ask?")
    print("""1) What is osu!\n2) What is the goal of this project\n3) What is Lazer and stable leaderboard\n4) What does the beatmap stats tells me?\n5) What does the leaderboard tells me?\n6) What is gamemode?\n7) What is hit judgement?\n8) What is mods?\n9) Why mods_to_num function exist\n10) What's the deal with 'CL'(Classic mod)?""")
    print('type "end" if you want to go back to leaderboard look-up')
    while True:
        question = input("Your question, input as integer: ")
        match question:
            case '1':
                print('osu! is a free to play online rhythm game hosted at https://osu.ppy.sh/, the game offers wide variety of "beatmaps" or levels made by members of the community with players competing with each other via "performance points (pp for short) and leaderboard position on maps.')
            case '2':
                print("The goal of this project is to display a leaderboard past top 50, which is the website's limit and allow users to view mods specific leaderboards which are locked behind pay wall (osu! supporter) though this is completely allowed by the dev of the game otherwise the API endpoint would not exist\nMore info : https://osu.ppy.sh/store/products/208")
            case '3':
                print('osu! has two clients "Lazer" which is a new client and "Stable" which is an old client. When the "Lazer" client was made allow to enter leaderboards it was decided that, "Stable" scores would be viewable on Lazer but "Lazer" scores would not be viewable on Stable\nnot only that but Lazer also have different scoring metric compare to stable. Stable uses exponential scoring based on combo while Lazer cap the score at 1 million which based of combo and accuracy\n Lastly, the classic mod, which will be explain on question 8\nMore info : https://osu.ppy.sh/home/download')
            case '4':
                print("The beatmap stats are Gamemode (see question 6)\nStar rating - The metric which tells you how difficult the map is, the higher the more difficult\ndifficulty's name - The name of the map difficulty which given by the creator of the map\nMap's ID every map has its own corresponding IDs (please don't confuse it with set's ID, the set's ID will contain multiple or single map's ID)\n For 4 other stats, please check https://osu.ppy.sh/wiki/en/Client/Beatmap_editor/Song_setup#difficulty")
            case '5':
                print("The leaderboard of a map are sorted by scores which determined by combo and accuracy\nThe grade of a scores are determined by accuracy, mod used and miss count of the map\nAccuracy are determined by hit judgement (300,100,50,miss) different game modes have different hit judgement, In this project only osu! gamemode's hit judgement is considered\nPP (Performance Points) are determined by combo,accuracy,misses that a player has made")
            case '6':
                print("osu! has 4 gamemode osu! which is the main gamemode Taiko, Ctb(Catch The Beat), Mania\nMore info : https://osu.ppy.sh/wiki/en/Game_mode")
            case '7':
                print("Hit judgement are the reward when a player hits an object on a map, which use to calculate accuracy of a score. Different gamemodes has different hit judgement but in this project only the osu! gamemode is supported though all other info is 100% supported\nMore info : https://osu.ppy.sh/wiki/en/Gameplay/Judgement")
            case '8':
                print("Mods are modifications that makes a map harder or easier such as DT(Double Time) which speeds up the map by 1.5*\nMore info : https://osu.ppy.sh/wiki/en/Gameplay/Game_modifier")
            case '9':
                print("In the library ossapi, the mods combination are determined by different value added on top of each other\nMore info : https://github.com/ppy/osu-api/wiki#mods")
            case '10':
                print('''Scores that are set on "Stable" client when ported to Lazer would automatically have "Classic mod" applied This in itself isn't problematic but,\nosu! api have changed its data structure to contain the Lazer version of the score which mean that "Stable" leaderboard would have Classic mod, which isn't supposed to happen so the function mod_acronym_cleanup is made to fix that''')
            case "end":
                print("Thank you for reading our FAQ\n")
                break
            case _:
                print('input the number of the question, type "end" if you want to go back')

def spacer(): #for the sake of visuals
    print()
    print("-----------------------------------------------------------------------\n")
    
def mapset_lookup(map_set_ID): #return beatmap info, check if it's valid
    try:
        status = api.beatmapset(map_set_ID).ranked #check the status if it has a leaderboard
        if status.value in Leaderboard_available:
            return "This beatmapset has leaderboard" #valid status 
        else:
            return "This beatmapset does not has leaderboard, try again"
    except:
        return "This beatmapset ID does not exist, try again"
    
def map_difficulties_and_stats(map_set_ID): #Display available difficulties and its stats
    betamapset_raw_data = api.beatmapset(map_set_ID).beatmaps #return beatmaps'ID as list
    for data in betamapset_raw_data: #looping through every map in a set
        ID_map = data.id #fetch the ID of each map
        map_info = api.beatmap(ID_map) #fetch the beatmap info with given ID
        star_rating = map_info.difficulty_rating
        difficulty_name = map_info.version
        game_mode = (map_info.mode).value
        cs = map_info.cs
        hp = map_info.drain
        ar = map_info.ar
        od = map_info.accuracy
        available_difficulties.append([game_mode,star_rating,difficulty_name,cs,hp,ar,od,ID_map])
    return available_difficulties #output as list to be display in pandas
    
def leaderboard_lookup(map_ID, mods_int, limit_input, legacy_leaderboard): #Display leaderboard of the beatmap's top 100
    rank = 0
    ranking_data = api.beatmap_scores(map_ID, mods=mods_int, limit=limit_input, legacy_only=legacy_leaderboard).scores #syntax specified, .scores attribute return list of scores in a map
    for data in ranking_data: #looping through every scores fetched
        raw_mod_acronym = "" #resets acronym every loop
        user_id = data.user_id
        rank += 1 #the API already sort the rank so using += 1 make sense as it would match the actual leaderboad anyway
        grade = (data.rank).value
        score = data.classic_total_score
        accuracy = round((data.accuracy)*100,2) #accuracy return as 0.xx with many digits, we only want 4 significant figures
        user = api.user(user_id).username #different class used
        combo = data.max_combo
        acc_stat = data.statistics
        hit_300 = acc_stat.great
        hit_100 = acc_stat.ok
        hit_50 = acc_stat.meh
        miss = acc_stat.miss
        pp = data.pp
        mods = data.mods
        score_ID = data.id
        if len(mods) == 0: raw_mod_acronym = 'NM' #if the score has no mod, display as NM
        else:
            for mod in range(len(mods)): #attribute .acronym only accept 1 value, which had to be looped
                raw_mod_acronym += ((mods)[mod]).acronym
        if hit_100 == None: hit_100 = 0 #Display as 0 in order to replicate actual leaderboard
        if hit_50 == None: hit_50 = 0
        if miss == None: miss = 0

        leaderboard.append([rank,grade,score,accuracy,user,combo,hit_300,hit_100,hit_50,miss,pp,raw_mod_acronym,score_ID])
    return leaderboard #output as list to be display by pandas
    
def mods_input_to_num(mods_input): #turn mods combination input into an integer (require file read)
    mods_int = 0
    Mods_file = open("Mods.txt", "r") 
    for line in Mods_file:
        mod, value = line.split()
        available_mods[mod] = int(value) #I use dict here
    for mod_input in mods_input:
        if mod_input in available_mods:
            mods_int += available_mods[mod_input]
    return mods_int

def mods_acronym_cleanup(leaderboard): #Cl mods had to convert to NM for stable leaderboard
    for ranking in leaderboard:
        if len(ranking[11]) == 2: #if the score only has a single mod
            if ranking[11] == "CL":
                ranking.pop(11)
                ranking.insert(11,"NM")
        if len(ranking[11]) > 2: #if the score has 2 mods or more with Classic in one of them
            if "CL" in ranking[11]:         
                ranking[11] = ranking[11].replace("CL","")
    return leaderboard

#variable declaration
Leaderboard_available = [1,2,3,4] #beatmap's status are represent in integers
available_difficulties = []
available_map_IDs = []
leaderboard = []
available_mods = {}
mod_list = ['NF', 'EZ', 'TD', 'HD', 'HR', 'SD', 'DT', 'HT', 'NC', 'FL', 'SP', 'PF', '4K', '5K', '10K', '8K', 'FI', '9K', '1K', '3K', '2K', 'MR', 'CL']
mods_input = None
#in order to not be confused with class' attributes, "beatmap" is shorten to "map" and beatmapset shorten to "map_set" for variables

while True: #loop until user inputs a valid api key
    client_ID = input("Enter your client ID : ").strip()
    client_secret = input("Enter your client secret : ").strip()
    print(API_Validity(client_ID,client_secret))
    if API_Validity(client_ID,client_secret) == "Valid":
        break
api = Ossapi(client_ID,client_secret)
spacer()

print("Hello welcome to osu! leaderboard look-up\nWould you like to check our FAQ first? (recommended)")
enter_faq = input("type 1 to say yes, left blank to say no : ")
if enter_faq == '1':
    FAQ()
        

while True: #loop until user picks a beatmap with leaderboard
    map_set_ID = input("Please input beatmapset ID : ").strip()
    print(mapset_lookup(map_set_ID))
    if mapset_lookup(map_set_ID) == "This beatmapset has leaderboard":
        break

print("Nice! let's see the difficulties of the mapset (please wait, it can take up to 30 seconds with 100 difficulties)")
available_difficulties = map_difficulties_and_stats(map_set_ID)
available_difficulties.sort() #sort by gamemodes and star ratings
beatmapset_display = pd.DataFrame(available_difficulties, columns=['Gamemode','star rating',"difficulty's name",'cs','hp','ar','od','beatmap ID'])
spacer()

print(beatmapset_display)
for difficulties in available_difficulties:
    available_map_IDs.append(difficulties[7])

print("Note : only the gamemode osu!'s hit judgement is supported (read FAQ 7)\nYou can still view other gamemode's leaderboard but the hit judgement will not be displayed correctly\nThough other info are unaffected and matched with the website, Thank you for understanding")
spacer()
    
print("please enter the following infomation to check the leaderboard")
while True: #the fool-proof method to ensure that the ID is valid
    map_ID = int(input("beatmap ID : "))
    if map_ID not in available_map_IDs:
        print("please enter the above's beatmap ID")   
    else:
        break
    
print("Stable or Lazer leaderboard (check FAQ for info)")
while True: #loop until no error
    legacy_input = input("type 1 for Stable, 2 for Lazer : ").strip()
    limit_input = int(input("how many position to display (100 max, integer only) : "))
    match legacy_input:
        case '1':
            legacy_leaderboard = True
        case '2':
            legacy_leaderboard = None #syntax specified
        case _:
            legacy_leaderboard = False #as in False input
            print("please only input 1 or 2")
    if limit_input > 100 or limit_input < 0:
        print("the limit is off-limit or goes negative")
    if (legacy_leaderboard == True or legacy_leaderboard == None) and 100 >= limit_input >= 1:
        break
    
mods_leaderboard = input("Do you want mods specific leaderboard? (type 1 for yes, left blank for no): ").strip()
if mods_leaderboard == "1":
    while True: #loop until all mods are valid
        error = ""
        mods_input = input("Please enter mods combination in acronym, seperated by space eg.(HD DT HR): ")
        mods_input = (mods_input.upper()).split() 
        for mods in mods_input:
            if mods not in mod_list:
                print(f"{mods} isn't a real mod")
                error = "yes"
        if error == "": #if no error, run the function
            mods_int = mods_input_to_num(mods_input)
            break
else:
    mods_int = mods_input
            
print("Let's begin leaderboard fetching, this will take awhile depending on the limit of positions")
leaderboard = leaderboard_lookup(map_ID, mods_int, limit_input, legacy_leaderboard)
if legacy_leaderboard == True: #if user wants stable leaderboard, run the clean up function
    leaderboard = mods_acronym_cleanup(leaderboard)
spacer()

print("Note : only osu! gamemode will display a correct hit judgement due to different gameplay structure in other gamemodes\nthough other info are unaffected and matched with the website\nNote 2 : There may be some users appear as 'DeletedUser' on the website but the API would not fetch them due to unavailable endpoint\n")
leaderboard_display = pd.DataFrame(leaderboard, columns=['Rank','Grade','Score','Accuracy','Player','Max combo','300','100','50','miss','PP','Mods','score ID'])
print(leaderboard_display)