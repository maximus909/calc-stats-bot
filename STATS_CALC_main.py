import json
import os
import logging
import traceback
from STATS_CALC_config import TOKEN, DIR, ADMIN_ID, SUPER_ADMIN_ID, CHANNEL_ID
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from emoji import emojize

updater = Updater(token=TOKEN, use_context = True)
dispatcher = updater.dispatcher

morning_time = emojize(':full_moon_with_face:', use_aliases=True)
day_time = emojize(':sun_with_face:', use_aliases=True)
night_time = emojize(':new_moon_with_face:', use_aliases=True)

skala = emojize(':black_heart:', use_aliases=True)
oplot = '☘️'#emojize(':shamrock:', use_aliases=True)
night = emojize(':bat:', use_aliases=True)
roza = emojize(':rose:', use_aliases=True)
amber = emojize(':maple_leaf:', use_aliases=True)
ferma = emojize(':eggplant:', use_aliases=True)
tortuga = emojize(':turtle:', use_aliases=True)

crossed_swords = emojize(':crossed_swords:', use_aliases=True)
shield = emojize(':shield:', use_aliases=True)
zp = emojize(':sunglasses:', use_aliases=True)
ga = emojize(':trident:', use_aliases=True)
lightning = emojize(':zap:', use_aliases=True)
easydef = emojize(':ok_hand:', use_aliases=True)
sleepingFace = emojize(':sleeping:', use_aliases=True)
fire = emojize(':fire:', use_aliases=True)
moneybag = emojize(':moneybag:', use_aliases=True)
res = emojize(':package:', use_aliases=True)
heart = emojize(':heart:', use_aliases=True)

BATTLE_STATS, CHOOSE_REPORT_TYPE, ATTACK_REPORT, DEFENCE_REPORT, CALC_ATTACK, CALC_DEFENCE = range(6)

bs = ''
breachedCastle = ''
protectedCastle = ''
day = ''
month = ''
year = ''
time = ''
breachedCastleInfo = {}
protectedCastleInfo = {}

# service

def isAdmin(id):
    return id in ADMIN_ID

def isSuperAdmin(id):
    return id in SUPER_ADMIN_ID

def representsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

# end service

def unknown(update, context):
    context.bot.send_message(update.effective_chat.id, '¯\\_(ツ)_/¯')

def start(update, context):
    chat_id = update.effective_chat.id
    if not isAdmin(chat_id):
        context.bot.send_message(chat_id, 'You are not admin. Please contact @magnusmax for an access.')
        return ConversationHandler.END
    else:
        context.bot.send_message(chat_id, 'Hello. I can calculate damage or defence for a certain battle.\nPlease forward me battle stats from @ChatWarsDigestsBot or type /use_prev to use previously submitted battle stats.')
    return BATTLE_STATS

def saveBattleStats(update, context):
    global day
    global month
    global year
    global time
    global bs
    d = {}
    d['breached'] = []
    d['protected'] = []
    chat_id = update.effective_chat.id
    message = update.message.text
    username = update.effective_chat.username
    if username is None:
        suffix = chat_id
    else:
        suffix = username
    if message == '/cancel':
        cancel(update, context)
        return ConversationHandler.END
    elif message == '/use_prev' and len(bs) != 0:
        text = 'Following battle stats will be used:\n'
        try:
            with open(bs, 'r', encoding='utf-8') as json_file:
                d = json.load(json_file)
            for i in range(len(d['breached'])):
                text = text + (d['breached'][i]['dayTime'] + '\n' if i == 0 else '') + d['breached'][i]['castle'] + ' <code>' + d['breached'][i]['points'] + '</code> ' + d['breached'][i]['breachType'] + ' ' + d['breached'][i]['gold'] + moneybag + '\n'
            for i in range(len(d['protected'])):
                text = text + d['protected'][i]['castle'] + ' <code>' + d['protected'][i]['points'] + '</code> ' + d['protected'][i]['breachType'] + ' ' + d['protected'][i]['gold'] + moneybag + '\n'
            reply_keyboard = [[crossed_swords + 'Attack', shield + 'Defence']]
            context.bot.send_message(
                chat_id=chat_id, 
                text= text + '\n' + 'Please choose what stats you want to calculate?', 
                reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
                parse_mode='HTML')
            return CHOOSE_REPORT_TYPE
        except Exception:
            logging.error(traceback.format_exc())
    elif message == '/use_prev' and len(bs) == 0:
        text = 'Following battle stats will be used:\n'
        filesList = []
        for subdir, dirs, files in os.walk(DIR):
            for f in files:
                if f.find(suffix) > 0:
                    filesList.append(f)
        lastFile = max(filesList)
        try:
            bs = DIR + lastFile
            print(bs)
            with open(bs, 'r', encoding='utf-8') as json_file:
                d = json.load(json_file)
            for i in range(len(d['breached'])):
                text = text + (d['breached'][i]['dayTime'] + '\n' if i == 0 else '') + d['breached'][i]['castle'] + ' <code>' + d['breached'][i]['points'] + '</code> ' + d['breached'][i]['breachType'] + ' ' + d['breached'][i]['gold'] + moneybag + '\n'
            for i in range(len(d['protected'])):
                text = text + d['protected'][i]['castle'] + ' <code>' + d['protected'][i]['points'] + '</code> ' + d['protected'][i]['breachType'] + ' ' + d['protected'][i]['gold'] + moneybag + '\n'
            reply_keyboard = [[crossed_swords + 'Attack', shield + 'Defence']]
            context.bot.send_message(
                chat_id=chat_id, 
                text= text + '\n' + 'Please choose what stats you want to calculate?', 
                reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
                parse_mode='HTML')
            return CHOOSE_REPORT_TYPE
        except Exception:
            logging.error(traceback.format_exc())

    elif update.message.forward_from == None or (update.message.forward_from != None and update.message.forward_from.id != 924278817):
        context.bot.send_message(chat_id, 'Please forward me battle stats from @ChatWarsDigestsBot. To cancel type /cancel')
        return BATTLE_STATS
    else:
        fullBattleStats = message.split('\n\n')
        day = fullBattleStats[0][2:4]
        month = fullBattleStats[0][5:7]
        year = '2020'
        if fullBattleStats[0][0] == morning_time:
            time = '09:00'
        elif fullBattleStats[0][0] == day_time:
            time = '17:00'
        elif fullBattleStats[0][0] == night_time:
            time = '01:00'
        else:
            time = '???'
        dayTime = day + '.' + month + '.' + year + ' ' + time
        bs = DIR + year + month + day + '_' + time[0:2] + '00_' + 'bs_' + suffix + '.json'

        if 'breached' in fullBattleStats[1]:
            breachedCastles = fullBattleStats[2].splitlines()
            try:
                for i in range(len(breachedCastles)):
                    if len(breachedCastles[i].split(' ')) == 3:
                        gold = '0'
                        castle, points, breachType = breachedCastles[i].split(' ')
                    else:
                        castle, points, breachType, gold = breachedCastles[i].split(' ')
                        gold = gold[:-1]
                    #d[castle] = {'dayTime':dayTime, 'breachType':breachType, 'points':points, 'gold':gold, 'damage':0}
                    d['breached'].append({'castle':castle, 'dayTime':dayTime, 'breachType':breachType, 'points':points, 'gold':gold, 'damage':0})
            except Exception:
                logging.error(traceback.format_exc())
        elif 'breached' in fullBattleStats[3]:
            breachedCastles = fullBattleStats[4].splitlines()
            for i in range(len(breachedCastles)):
                if len(breachedCastles[i].split(' ')) == 3:
                    gold = '0'
                    castle, points, breachType = breachedCastles[i].split(' ')
                else:
                    castle, points, breachType, gold = breachedCastles[i].split(' ')
                    gold = gold[:-1]
                d['breached'].append({'castle':castle, 'dayTime':dayTime, 'breachType':breachType, 'points':points, 'gold':gold, 'damage':0})
        else:
            print('???')
        
        if 'protected' in fullBattleStats[1]:
            breachedCastles = fullBattleStats[2].splitlines()
            for i in range(len(breachedCastles)):
                if len(breachedCastles[i].split(' ')) == 3:
                    gold = '0'
                    castle, points, breachType = breachedCastles[i].split(' ')
                else:
                    castle, points, breachType, gold = breachedCastles[i].split(' ')
                    gold = gold[:-1]
                d['protected'].append({'castle':castle, 'dayTime':dayTime, 'breachType':breachType, 'points':points, 'gold':gold, 'protection':0})
        elif 'protected' in fullBattleStats[3]:
            breachedCastles = fullBattleStats[4].splitlines()
            for i in range(len(breachedCastles)):
                if len(breachedCastles[i].split(' ')) == 3:
                    gold = '0'
                    castle, points, breachType = breachedCastles[i].split(' ')
                else:
                    castle, points, breachType, gold = breachedCastles[i].split(' ')
                    gold = gold[:-1]
                d['protected'].append({'castle':castle, 'dayTime':dayTime, 'breachType':breachType, 'points':points, 'gold':gold, 'protection':0})
        else:
            print('???')

        if not os.path.isfile(bs):
            with open(bs, 'w', encoding='utf-8') as file:
                json.dump(d, file, indent=4, ensure_ascii=False)

        reply_keyboard = [[crossed_swords + 'Attack', shield + 'Defence']]
        context.bot.send_message(
            chat_id=chat_id, 
            text='Please choose what stats you want to calculate?', 
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        return CHOOSE_REPORT_TYPE

def chooseReportType(update, context):
    chat_id = update.effective_chat.id
    message = update.message.text
    #reply_keyboard = [[tortuga, roza, amber], [ferma, oplot, night], [skala]]
    row1 = []
    row2 = []
    row3 = []
    if message == crossed_swords + 'Attack':
        with open(bs, 'r', encoding='utf-8') as json_file:
            d = json.load(json_file)
        #ls = []
        for i in range(len(d['breached'])):
            if i < 3:
                row1.append(d['breached'][i]['castle'])
            elif i < 6:
                row2.append(d['breached'][i]['castle'])
            else:
                row3.append(d['breached'][i]['castle'])
        reply_keyboard = [row1, row2, row3]
        context.bot.send_message(
            chat_id,
            'Please choose a castle:',
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return ATTACK_REPORT
    elif message == shield + 'Defence':
        with open(bs, 'r', encoding='utf-8') as json_file:
            d = json.load(json_file)
        #ls = []
        for i in range(len(d['protected'])):
            if i < 3:
                row1.append(d['protected'][i]['castle'])
            elif i < 6:
                row2.append(d['protected'][i]['castle'])
            else:
                row3.append(d['protected'][i]['castle'])
        reply_keyboard = [row1, row2, row3]
        context.bot.send_message(
            chat_id,
            'Please choose a castle:',
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return DEFENCE_REPORT
    else:
        #context.bot.send_message(chat_id, 'Wrong input. Try again /start.', reply_markup = ReplyKeyboardRemove())
        #return ConversationHandler.END
        context.bot.send_message(chat_id, 'Wrong input. Please choose what stats you want to calculate? To cancel type /cancel')
        return CHOOSE_REPORT_TYPE

def getAttackReport(update, context):
    global breachedCastle
    global breachedCastleInfo
    chat_id = update.effective_chat.id
    breachedCastle = update.message.text
    if not breachedCastle in tortuga+roza+amber+ferma+oplot+night+skala:
        #context.bot.send_message(chat_id, 'Worng input. Try again /start.', reply_markup = ReplyKeyboardRemove())
        #return ConversationHandler.END
        context.bot.send_message(chat_id, 'Worng input. Please choose a castle. To cancel type /cancel')
        return ATTACK_REPORT
    else:
        try:
            with open(bs, 'r', encoding='utf-8') as json_file:
                d = json.load(json_file)
                for i in range(len(d['breached'])):
                    if d['breached'][i]['castle'] == breachedCastle:
                        breachedCastleInfo[breachedCastle] = {'dayTime': d['breached'][i]['dayTime'], 'breachType': d['breached'][i]['breachType'], 'points': d['breached'][i]['points'], 'gold': d['breached'][i]['gold'], 'damage': d['breached'][i]['damage']}
                #print(breachedCastleInfo)
        except Exception:
            logging.error(traceback.format_exc())

    context.bot.send_message(update.effective_chat.id, 'Please send the attack report or just attack and gold from the report, e.g. 240 24.', reply_markup = ReplyKeyboardRemove())
    return CALC_ATTACK
'''
def calcAttackTest(update, context):
    global breachedCastleInfo
    chat_id = update.effective_chat.id
    message = update.message.text
    try:
        if 'Твои результаты в бою' in message:
            attack = message[message.find(':')+1:message.find(' ', message.find(':')+1)]
            if attack.find('(') != -1:
                attack = attack[:attack.find('(')]
            defence = message[message.find(shield+':')+2:message.find(' ', message.find(shield+':')+2)]
            if defence.find('(') != -1:
                defence = defence[:defence.find('(')]
            #exp = message[message.find(':', message.find(fire))+2:message.find('\n', message.find(fire))]
            goldReport = message[message.find(':', message.find(moneybag))+2:message.find('\n', message.find(moneybag))]
            #stock = message[message.find(':', message.find(res))+2:message.find('\n', message.find(res))]
            #hp = message[message.find(':', message.find(heart))+2:]
            #print(crossed_swords)
            text = attack + '\n' + defence + '\n' + goldReport
            print(message)
            context.bot.send_message(chat_id, text)
            return ConversationHandler.END
        else:
            context.bot.send_message(chat_id, 'Wrong input. Try again /start.')
            return ConversationHandler.END
    except Exception:
        logging.error(traceback.format_exc())
'''

def calcAttack(update, context):
    global breachedCastleInfo
    chat_id = update.effective_chat.id
    message = update.message.text
    try:
        if 'Твои результаты в бою' in message:
            attack = message[message.find(':')+1:message.find(' ', message.find(':')+1)]
            if attack.find('(') != -1:
                attack = attack[:attack.find('(')]
            #attack = message[message.find(crossed_swords+':')+2:message.find(' ', message.find(crossed_swords+':')+2)]
            #defence = message[message.find(shield+':')+2:message.find(' ', message.find(shield+':')+2)]
            #exp = message[message.find(':', message.find(fire))+2:message.find('\n', message.find(fire))]
            goldReport = message[message.find(':', message.find(moneybag))+2:message.find('\n', message.find(moneybag))]
            #stock = message[message.find(':', message.find(res))+2:message.find('\n', message.find(res))]
            #hp = message[message.find(':', message.find(heart))+2:]
            breachedCastleInfo[breachedCastle]['damage'] = int(-1 * (int(attack) / int(goldReport)) * int(breachedCastleInfo[breachedCastle]['gold']))
            with open(bs, 'r', encoding='utf-8') as json_file:
                d = json.load(json_file)
            for i in range(len(d['breached'])):
                if d['breached'][i]['castle'] == breachedCastle:
                    d['breached'][i]['damage'] = breachedCastleInfo[breachedCastle]['damage']
            with open(bs, 'w', encoding='utf-8') as file:
                json.dump(d, file, indent=4, ensure_ascii=False)
            context.bot.send_message(chat_id, 'Attack: ' + str(breachedCastleInfo[breachedCastle]['damage']) + '. Data is saved.\nTo form a report type /report YYYY MM DD HH')
            return ConversationHandler.END
        elif message.find(' ') != -1 and len(message.split(' ')) == 2 and representsInt(message.split(' ')[0]) and representsInt(message.split(' ')[1]): 
            attack, goldReport = message.split(' ')
            breachedCastleInfo[breachedCastle]['damage'] = int(-1 * (int(attack) / int(goldReport)) * int(breachedCastleInfo[breachedCastle]['gold']))
            with open(bs, 'r', encoding='utf-8') as json_file:
                d = json.load(json_file)
            for i in range(len(d['breached'])):
                if d['breached'][i]['castle'] == breachedCastle:
                    d['breached'][i]['damage'] = breachedCastleInfo[breachedCastle]['damage']
            with open(bs, 'w', encoding='utf-8') as file:
                json.dump(d, file, indent=4, ensure_ascii=False)
            context.bot.send_message(chat_id, 'Attack: ' + str(breachedCastleInfo[breachedCastle]['damage']) + '. Data is saved.\nTo form a report type /report YYYY MM DD HH')
            return ConversationHandler.END
        else:
            context.bot.send_message(chat_id, 'Wrong input. Please send the attack report or just attack and gold from the report, e.g. 240 24. To cancel type /cancel')
            return CALC_ATTACK
    except Exception:
        logging.error(traceback.format_exc())

def getDefenceReport(update, context):
    global protectedCastle
    global protectedCastleInfo
    chat_id = update.effective_chat.id
    protectedCastle = update.message.text
    if not protectedCastle in tortuga+roza+amber+ferma+oplot+night+skala:
        context.bot.send_message(chat_id, 'Worng input. Please choose a castle. To cancel type /cancel')
        return DEFENCE_REPORT
    else:
        try:
            with open(bs, 'r', encoding='utf-8') as json_file:
                d = json.load(json_file)
                for i in range(len(d['protected'])):
                    if d['protected'][i]['castle'] == protectedCastle:
                        protectedCastleInfo[protectedCastle] = {'dayTime': d['protected'][i]['dayTime'], 'breachType': d['protected'][i]['breachType'], 'points': d['protected'][i]['points'], 'gold': d['protected'][i]['gold'], 'protection': d['protected'][i]['protection']}
                #print(protectedCastleInfo)
        except Exception:
            logging.error(traceback.format_exc())

    context.bot.send_message(update.effective_chat.id, 'Please send the defence report or just defence and gold from the report, e.g. 350 14.', reply_markup = ReplyKeyboardRemove())
    return CALC_DEFENCE

def calcDefence(update, context):
    global protectedCastleInfo
    chat_id = update.effective_chat.id
    message = update.message.text
    try:
        if 'Твои результаты в бою' in message:
            #attack = message[message.find(crossed_swords+':')+2:message.find(' ', message.find(crossed_swords+':')+2)]
            defence = message[message.find(shield+':')+2:message.find(' ', message.find(shield+':')+2)]
            if defence.find('(') != -1:
                defence = defence[:defence.find('(')]
            #exp = message[message.find(':', message.find(fire))+2:message.find('\n', message.find(fire))]
            goldReport = message[message.find(':', message.find(moneybag))+2:message.find('\n', message.find(moneybag))]
            #stock = message[message.find(':', message.find(res))+2:message.find('\n', message.find(res))]
            #hp = message[message.find(':', message.find(heart))+2:]
            protectedCastleInfo[protectedCastle]['protection'] = int(int(protectedCastleInfo[protectedCastle]['gold']) / (int(goldReport) / int(defence)))
            with open(bs, 'r', encoding='utf-8') as json_file:
                d = json.load(json_file)
            for i in range(len(d['protected'])):
                if d['protected'][i]['castle'] == protectedCastle:
                    d['protected'][i]['protection'] = protectedCastleInfo[protectedCastle]['protection']
            with open(bs, 'w', encoding='utf-8') as file:
                json.dump(d, file, indent=4, ensure_ascii=False)
            context.bot.send_message(chat_id, 'Defence: ' + str(protectedCastleInfo[protectedCastle]['protection']) + '. Data is saved.\nTo form a report type /report YYYY MM DD HH')
            return ConversationHandler.END
        elif message.find(' ') != -1 and len(message.split(' ')) == 2 and representsInt(message.split(' ')[0]) and representsInt(message.split(' ')[1]):
            defence, goldReport = message.split(' ')
            protectedCastleInfo[protectedCastle]['protection'] = int(int(protectedCastleInfo[protectedCastle]['gold']) / (int(goldReport) / int(defence)))
            with open(bs, 'r', encoding='utf-8') as json_file:
                d = json.load(json_file)
            for i in range(len(d['protected'])):
                if d['protected'][i]['castle'] == protectedCastle:
                    d['protected'][i]['protection'] = protectedCastleInfo[protectedCastle]['protection']
            with open(bs, 'w', encoding='utf-8') as file:
                json.dump(d, file, indent=4, ensure_ascii=False)
            context.bot.send_message(chat_id, 'Defence: ' + str(protectedCastleInfo[protectedCastle]['protection']) + '. Data is saved.\nTo form a report type /report YYYY MM DD HH')
            return ConversationHandler.END
        else:
            context.bot.send_message(chat_id, 'Wrong input. Please send the defence report or just defence and gold from the report, e.g. 350 14. To cancel type /cancel')
            return CALC_DEFENCE
    except Exception:
        logging.error(traceback.format_exc())

def cancel(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id, 'To restart, press /start', reply_markup = ReplyKeyboardRemove())
    return ConversationHandler.END

def report(update, context):
    chat_id = update.effective_chat.id
    message = update.message.text
    username = update.effective_chat.username
    if username is None:
        suffix = chat_id
    else:
        suffix = username
    if not isAdmin(chat_id):
        context.bot.send_message(chat_id, 'You are not admin. Please contact @magnusmax for an access.')
        return
    else:
        if message.find(' ') == -1:
            context.bot.send_message(chat_id, 'Invalid format. Type /report YYYY MM DD HH')
            return
        command, year, month, day, time = message.split(' ')
        bs = DIR + year + month + day + '_' + time + '00_' + 'bs_' + suffix + '.json' 
        try:
            with open(bs, 'r', encoding='utf-8') as json_file:
                d = json.load(json_file)
            text = day + '.' + month + '.' + year + ' ' + time +':00' + '\n'
            total_dmg = 0
            for i in range(len(d['protected'])):
                if d['protected'][i]['breachType'] != easydef and d['protected'][i]['breachType'] != sleepingFace:
                    text = text + d['protected'][i]['castle'] + ':' + d['protected'][i]['breachType'] + (shield if d['protected'][i]['breachType'] == ga else '') + str(round(d['protected'][i]['protection']/1000,1)) + 'k\n'
                    total_dmg = total_dmg + round(d['protected'][i]['protection']/1000,1)
            for i in range(len(d['breached'])):
                text = text + d['breached'][i]['castle'] + ':' + d['breached'][i]['breachType'] + str(round(d['breached'][i]['damage']/1000,1)) + 'k\n'
                total_dmg = total_dmg + round(d['breached'][i]['damage']/1000,1)
            text = text + 'Total dmg: ' + str(round(total_dmg,1)) + 'k'
            #print(text)
            context.bot.send_message(chat_id, text)
        except Exception:
            logging.error(traceback.format_exc())

def msg(update, context):
    context.bot.send_message(update.effective_chat.id, '¯\\_(ツ)_/¯')
    '''
    if not update.message.reply_to_message is None:
        replied_info = update.message.reply_to_message
        context.bot.send_message(chat_id, str(replied_info))
    '''

def send(update, context):
    chat_id = update.effective_chat.id
    if not isSuperAdmin(chat_id):
        context.bot.send_message(chat_id, 'You are not admin. Please contact @magnusmax for an access.')
    elif update.message.reply_to_message is None:
        context.bot.send_message(chat_id, 'You have to reply on the message to forward it.')
    else:
        replied_info = update.message.reply_to_message
        try:
            if 'Total dmg:' in replied_info.text:
                context.bot.forward_message(CHANNEL_ID, chat_id, replied_info.message_id)
            else:
                context.bot.send_message(chat_id, 'It\'s not a summary.')
        except Exception:
            logging.error(traceback.format_exc())

start_handler = CommandHandler('start', start)
saveBattleStats_handler = MessageHandler(Filters.all, saveBattleStats)
chooseReportType_handler = MessageHandler(Filters.text, chooseReportType)
getAttackReport_handler = MessageHandler(Filters.text, getAttackReport)
getDefenceReport_handler = MessageHandler(Filters.text, getDefenceReport)
calcAttack_handler = MessageHandler(Filters.text, calcAttack)
calcDefence_handler = MessageHandler(Filters.text, calcDefence)
cancel_handler = CommandHandler('cancel', cancel)

stats_calc_conv_handler = ConversationHandler(
    entry_points = [start_handler],
    states={
        BATTLE_STATS: [saveBattleStats_handler],
        CHOOSE_REPORT_TYPE: [chooseReportType_handler],
        ATTACK_REPORT: [getAttackReport_handler],
        DEFENCE_REPORT: [getDefenceReport_handler],
        CALC_ATTACK: [calcAttack_handler],
        CALC_DEFENCE: [calcDefence_handler]

    },
    fallbacks=[cancel_handler]
)


dispatcher.add_handler(stats_calc_conv_handler)
'''
calcAttackTest_handler = MessageHandler(Filters.text, calcAttackTest)
dispatcher.add_handler(calcAttackTest_handler)
'''
report_handler = CommandHandler('report', report)
dispatcher.add_handler(report_handler)

send_handler = CommandHandler('send', send)
dispatcher.add_handler(send_handler)

msg_handler = MessageHandler(Filters.text, msg)
dispatcher.add_handler(msg_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

def main():
	updater.start_polling()
    #updater.idle()

if __name__ == '__main__':
    main()
