int lampka = 13;
int pzmieniacz = 6;
int lzmieniacz = 5;
int prelay = 4;
int lrelay = 3;
int receiveclose = A5;
int receiveopen = A4;
int openBtn = A2;
int closeBtn = A0;
int openlBtn = A3;
int openrBtn = A1;
int fotokomorkaPin = 8;  

void otworzBrame();
void zamknijBrame();

void setup() {
  pinMode(lampka, OUTPUT);
  pinMode(pzmieniacz, OUTPUT);
  pinMode(lzmieniacz, OUTPUT);
  pinMode(prelay, OUTPUT);
  pinMode(lrelay, OUTPUT);
  pinMode(receiveclose, INPUT);
  pinMode(receiveopen, INPUT);
  pinMode(openBtn, INPUT);
  pinMode(closeBtn, INPUT);
  pinMode(openlBtn, INPUT);
  pinMode(openrBtn, INPUT);
  pinMode(fotokomorkaPin, INPUT);  

  digitalWrite(lampka, LOW);
  digitalWrite(pzmieniacz, LOW);
  digitalWrite(lzmieniacz, LOW);
  digitalWrite(prelay, LOW);
  digitalWrite(lrelay, LOW);
}

void loop() {
  if ((digitalRead(openBtn) == HIGH || digitalRead(receiveopen) == HIGH) && digitalRead(fotokomorkaPin) == LOW) {
    otworzBrame();
    delay(500);
  }

  if ((digitalRead(closeBtn) == HIGH || digitalRead(receiveclose) == HIGH) && digitalRead(fotokomorkaPin) == LOW) {
    zamknijBrame();
    delay(500);
  }

  if (digitalRead(openlBtn) == HIGH && digitalRead(fotokomorkaPin) == LOW) {
    //otwieranie lewej ale narazie bez tego(trzeba byłoby zrobić w przypadku lewej aby prawa też się otwierała troche)
    delay(500);
  }

  if (digitalRead(openrBtn) == HIGH && digitalRead(fotokomorkaPin) == LOW ) {
     //otwieranie prawej ale narazie bez tego
    delay(500);
  
  }
}

void otworzBrame() {
  digitalWrite(lampka, HIGH);

  digitalWrite(pzmieniacz, LOW);
  digitalWrite(lzmieniacz, LOW);
  delay(500);

  digitalWrite(prelay, HIGH);
  delay(3000);  //czas pomiędzy startem pierwszej połówki a startem drugiej 
  digitalWrite(lrelay, HIGH);

  delay(5000); //czas otwierania bramy zmienić tak jak ma być

  digitalWrite(prelay, LOW);
  digitalWrite(lrelay, LOW);

  digitalWrite(lampka, LOW);
}

void zamknijBrame() {
  digitalWrite(lampka, HIGH);

  digitalWrite(lzmieniacz, HIGH);
  digitalWrite(pzmieniacz, HIGH);
  delay(500);

  digitalWrite(lrelay, HIGH);
  delay(3000);       //czas pomiędzy startem pierwszej połówki a startem drugiej 
  digitalWrite(prelay, HIGH);

  delay(5000); //czas zamykania bramy zmienić tak jak ma być

  digitalWrite(lrelay, LOW);
  digitalWrite(prelay, LOW);

  digitalWrite(lampka, LOW);
}
