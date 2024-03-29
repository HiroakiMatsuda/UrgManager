UrgManager
======================
UrgManagerは[北陽電機（株）][hokuyo]のレーザースキャナである[URGシリーズ][urg]を制御するRTコンポーネントです      
Python Moduleを使用した階層構造によりユーザー自身で改変が行いやすくなっています  
また、使用する計測モードや計測範囲などを簡単に設定することができます     

[hokuyo]: http://www.hokuyo-aut.co.jp/index.html
[urg]: http://www.hokuyo-aut.co.jp/02sensor/

動作確認環境
------
Python:  
2.6.6  

pySerial:  
2.6

OS:  
Windows 7 64bit / 32bit  
Ubuntu 10.04 LTS / 12.04 LTS 32bit

URG:  
UTM-30LX   


各コマンドは以下の[UTM-30LX 通信仕様書(SCIP2.0)][scip]に従って機能を提供しています  

[scip]: http://www.hokuyo-aut.co.jp/02sensor/07scanner/download/products/utm-30lx/ 

ファイル構成
------
UrgManager
│―UrgManager.py  
│―pyurg.py  
│―ini   
│　　│―urg.ini    
│  
│―rtc.conf  

* UrgManager.py  
RTC本体です  
* pyurg.py  
URGと通信を行うPython Moduleです  
このモジュールは付属しますが、[こちら][pyurg]でも配布されています   
[pyurg]: https://github.com/HiroakiMatsuda/pyurg  
 
* urg.ini  
計測するデータの種類や、計測範囲の設定を行います    
* rtc.conf  
ポートの設定や動作周期を設定できます  

注:本RTCにおいてユーザーが操作すると想定しているファイルのみ説明しています  

ファイルの設定はiniファイルを通して行えるので、簡単に設定を変えられます  
iniファイルの設定はActivate時に読み込まれるので、設定を変更した場合は一度Deactivateしたあとに再度Activateすることで変更されます  


RTCの構成
------  
<img src="http://farm9.staticflickr.com/8067/8272186899_878720eab5_c.jpg" width="500px" />

データポートは2つあり、以下のようになっています  
  
* command port :InPort  
データ型; TimedLongSeq   
[Command]  
 ・  `Command` :  動作状態の操作
0:URGの計測を中断し、設定をリセットします  
1:計測データの出力を行います  

* data port :OutPort  
データ型; TimedLongSeq  
urg.iniの[DATA]intens = OFF    
[Timestamp, 1, Dist_length, Dist1, Dist2..........., DistX]    
 ・  `Timestamp` :  URG内のタイムスタンプ     
アップカウントのタイマで、最大16777216 [ms]までカウント後、0にリセットされます   
 ・  `1` :  センサデータブロックの個数です  
距離データで2ブロックです       
 ・  `Dist_length` :  距離データの長さ  
スキャン個数分だけデータが続きます    
 ・  `Dist1~X` :  距離データ [mm]    

 urg.iniの[DATA]intens = ON  
[Timestamp, 2, Dist_length, Intens_length, Dist1, Dist2, ..., DistX,  Intens1, Intens2, ..., IntensX]  
 ・  `Timestamp` :  URG内のタイムスタンプ  
アップカウントのタイマで、最大16777216 [ms]までカウント後、0にリセットされます   
 ・  `2` :  センサデータブロックの個数です  
距離データと反射強度データで2ブロックです       
 ・  `Dist_length` :  距離データの長さ  
スキャン個数分だけデータが続きます    
 ・  `Intens_length` :  反射強度データの長さ  
スキャン個数分だけデータが続きます  
 ・  `Dist1~X` :  距離データ [mm]  
 ・  `Intens1~X` :  反射強度データ     

使い方：　MultiTypeConsoleOutを使用してテストする
------
###1. pySerialをインストールする###
pyrsは[pySerial](:http://pyserial.sourceforge.net/)を使用してシリアル通信を行なっています。  
pySerialがインストールされていない場合は、インストールしてから実行して下さい  

###2. URGの設定する###
urg.iniをテキストエディタなどで開き編集します  

**[PORT]**  
  ・ ```port = XXX```  
使用するシリアルポートの設定をします  
WindowsではCOM1、Ubuntuでは/def/ttyUSB0のように入力します  
  ・ ```baudrate = X```  
ボーレートを設定します。RSシリーズでは通常115200 [bi/sec]となっています  

**[DATA]**  
  ・ ```dist = XXX```  
距離データを出力するか決定します（現在のバージョンでは常にONとなります）    
ON:距離データ出力有り  
OFF:距離データ出力なし  
  ・ ```intens = XXX```  
反射強度データを出力するか決定します    
ON:反射強度データ出力有り  
OFF:反射強度データ出力なし  
  ・ ```command = XXX```  
コマンドを受け付けるか選択します    
ON:コマンドを受け付けて動作します。コマンドが入力されない限りデータは出力されません  
OFF:コマンドがなくてもデータが出力されますが、コマンドは認識できません      
  ・ ```amin = X```  
有効計測エリア開始ステップ番号を指定します  
  ・```amax = X```  
有効計測エリア終了ステップ番号を指定します 
 
  ・```num = X```  
計測回数を指定します。0~99で指定でき、0のときはcommand = 1を入力するまで計測を繰り返します   

これらの設定はActivate時に読み込まれるので、設定を変更した場合は一度Deactivateしたあとに再度Activateすることで変更されます  
 
###3. MultiTypeConsoleOutと接続する###
1. UrgManager.py起動する  
urg.iniを開き、[DATA] command = OFFとします。 これで計測データを自動的に出力するモードとなります  
次に、[DATA] num = 1とします。これは計測回数を指定しています  
その後、UrgManager.pyをダブルクリックするなどして起動してください  
2. データ表示用RTC MultiTypeConsoleOutを起動する    
consoleout.iniを開き、[DATA] type = TimedLongSeqに指定します  
これでMultiTypeConsoleInのデータ型はTimedLongSeq型となります  
その後、MultiTypeConsoleInをダブルクリックするなどして起動してください  
データ表示用RTCである[MultiTypeConsoleOut][console]と接続します 
MultiTypeConsoleOutは[ここ][console]からDLしてください   

[console]: https://github.com/HiroakiMatsuda/MultiTypeConsoleOut
  
###4. データを表示する###
接続が終わったら、2つのコンポーネントをActivateします      
Consoleにセンサが表示されれるのが確認できます  
計測回数や計測範囲、データの種別などを変えて試してみて下さい   
なお、膨大なデータを扱いますので、MultiTypeConsoleInのログ生成機能を使用して、Excelなどでプロットして確認することをおすすめします    
      
以上が本RTCの使い方となります  

ライセンス
----------
Copyright &copy; 2012 Hiroaki Matsuda  
Licensed under the [Apache License, Version 2.0][Apache]  
Distributed under the [MIT License][mit].  
Dual licensed under the [MIT license][MIT] and [GPL license][GPL].  
 
[Apache]: http://www.apache.org/licenses/LICENSE-2.0
[MIT]: http://www.opensource.org/licenses/mit-license.php
[GPL]: http://www.gnu.org/licenses/gpl.html