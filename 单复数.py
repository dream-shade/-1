while True:
    try :
        x=int(input('输入一个数'))
        if x&1==0:
            print("复数")#even
        else:
            print('单数')#odd
        #转换成2进制数
    except ValueError:
        print('滚你妈的')