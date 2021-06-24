import socket, sys

HOST = '127.0.0.1'
PORT = 20000
BUFFER_SIZE = 1024

class Players:
  def __init__(self, name1, name2, type1, type2):
    self.name1 = name1
    self.name2 = name2
    self.type1 = type1
    self.type2 = type2
    self.change = True

def makeBoard() :
    theBoard = {};
    rows = ['top','mid','low']
    cols = ['L','M','R']
    for r in rows :
        for c in cols :
            key = str(r) + '-' + str(c)
            theBoard.setdefault(key,False)
    #print('DEBUG: '+str(theBoard))
    return theBoard

def printCell(cell) :
    if cell : 
        return ' '+str(cell)+' '
    else :
        return '   '

def showBoard(board) : 
    print('\n=Tabuleiro=')
    print(printCell(board['top-L'])+'|'+printCell(board['top-M'])+'|'+printCell(board['top-R']))
    print('-----------')
    print(printCell(board['mid-L'])+'|'+printCell(board['mid-M'])+'|'+printCell(board['mid-R']))
    print('-----------')
    print(printCell(board['low-L'])+'|'+printCell(board['low-M'])+'|'+printCell(board['low-R']))

def determineVictory(board):
    rows = ['top','mid','low']
    cols = ['L','M','R']
    # se uma linha tiver todas as colunas iguais é vitoria
    for r in rows :
        col1 = str(r)+'-L'
        col2 = str(r)+'-M'
        col3 = str(r)+'-R'
        if board[col1] == board[col2] == board[col3] and bool(board[col1]) :
            return board[col3]
    # se uma coluna tiver todas as linhas iguais é vitoria
    for c in cols :
        row1 = 'top-'+str(c)
        row2 = 'mid-'+str(c)
        row3 = 'low-'+str(c)
        if board[row1] == board[row2] == board[row3] and bool(board[row1]) :
            return board[row3]
    # se houver uma diagonal com todas iguais então é vitoria
    middle = 'mid-M';
    sel1, sel2 = str(rows[0]+'-'+cols[2]), str(rows[2]+'-'+cols[0])
    if board[middle] == board[sel1] == board[sel2] :
       return board[middle]
    sel1, sel2 = str(rows[0]+'-'+cols[0]), str(rows[2]+'-'+cols[2])
    if board[middle] == board[sel1] == board[sel2] :
       return board[middle]
    return False

def determineAvailableMoves(board) :
    rows = ['top','mid','low']
    cols = ['L','M','R']
    hasMoves = False
    # verifica se posicão escolhida é válida
    for r in rows :
        for c in cols :
            key = str(r) + '-' + str(c)
            if not bool(board[key]) :
                return True
    return hasMoves

def readInputAndTryToPutOnBoard(board, player) :
    rows = ['top','mid','low']
    cols = ['L','M','R']
    if(player.change):
        print('\nJogador', player.name1, ' é a sua vez!!')
    else:
        print('\nJogador', player.name2, ' é a sua vez!!')
    
    print('\nPara fazer um movimento, digite uma linha (top, mid, low), seguido por um traço (-) e uma coluna (L, M, R). \nExemplo: top-M')
    move = input()
    valida = False
    # verifica se posicão escolhida é válida
    for r in rows :
        for c in cols :
            key = str(r) + '-' + str(c)
            if key == move :
                valida = True

    if valida & bool(board[move]):
        print('\nPosição já ocupada!');
        return False
    elif valida :
        if(player.change):
            board[move] = player.type1
        else:
            board[move] = player.type2

        return True
    else : 
        print('Posição inválida!');
        return False

def toString(board) :
    text = ('\n=Tabuleiro=')
    text = (text + '\n' + printCell(board['top-L'])+'|'+printCell(board['top-M'])+'|'+printCell(board['top-R']))
    text = (text + '\n' + '-----------')
    text = (text + '\n' + printCell(board['mid-L'])+'|'+printCell(board['mid-M'])+'|'+printCell(board['mid-R']))
    text = (text + '\n' + '-----------')
    text = (text + '\n' + printCell(board['low-L'])+'|'+printCell(board['low-M'])+'|'+printCell(board['low-R']))
    return text

def main(argv):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            
            print('\n======= Jogo da Velha =======\n')

            name1 = input("\nDigite seu nome jogador1: ")
            while (True):
                opc1 = input("Escolha X ou O: ")
                if opc1 == 'o' or opc1 == '0' or opc1 == 'O' or opc1 == 'X' or opc1 == 'x':
                    break
                else:
                    print("Escolha uma opção válida!!\n")
            
            name2 = input("\nDigite seu nome jogador2: ")
            if opc1 == 'X' or opc1 == 'x':
                print(name2," Você Jogará como O")
                opc2 = 'O'
            else:
                print(name2," Você Jogará como X")
                opc2 = 'X'
            
            player = Players(name1, name2, opc1, opc2)

            board = makeBoard();
            while True :
                showBoard(board);
                # Obtem movimento
                while True : 
                    move = readInputAndTryToPutOnBoard(board, player)
                    if move :
                        break
                # Verifica se movimento concedeu vitoria
                if determineVictory(board) :
                    showBoard(board);
                    if(player.change):
                        print('\nJogador '+player.name1+' Venceu!!!')
                    else:
                        print('\nJogador '+player.name2+' Venceu!!!')

                    return True
                # verifica se ainda há movimentos possíveis
                if not determineAvailableMoves(board) :
                    print('\nEmpate! Deu Velha!!!')
                    return True
                # Caso não tenha vencido então muda jogador e tenta denovo
                if(player.change):
                    player.change = False
                else:
                    player.change = True
                # Envia atualização do tabuleiro ao servidor
                text = toString(board)
                s.send(text.encode())
                data = s.recv(BUFFER_SIZE)
                received = repr(data)
                #print('Recebido do servidor', received)
                text_string = data.decode('utf-8')
                if (text_string == 'bye'):
                    print('vai encerrar o socket cliente!')
                    s.close()
                    break

    except Exception as error:
        print('Erro na execução o programa será encerrado!')
        print(error)
        return

if __name__ == '__main__':
    main(sys.argv[1:])


