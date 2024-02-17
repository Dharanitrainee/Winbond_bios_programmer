/* Author: Dharani mohan
 * Date: 10.02.2024*/

#include <Arduino.h>

#include <SPI.h>

#include <WINBOND.h>

void WINBOND::Reset() {
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(RESET);
  delayMicroseconds(100);
  digitalWrite(CS_PIN, HIGH);
}

void WINBOND::Release_Power_Down() {
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(R_POWER_DOWN);
  digitalWrite(CS_PIN, HIGH);
}

void WINBOND::Init(int CS_PIN) {
  SPI.begin();
  SPI.setBitOrder(MSBFIRST);
  SPI.setDataMode(SPI_MODE0);
  pinMode(CS_PIN, OUTPUT);
  digitalWrite(CS_PIN, HIGH);
  Reset();
  Release_Power_Down();
  WriteDisable();
}

void WINBOND::WriteEnable() {
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(WRITE_ENABLE);
  digitalWrite(CS_PIN, HIGH);
}

void WINBOND::WriteDisable() {
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(WRITE_DISABLE);
  digitalWrite(CS_PIN, HIGH);
}

void WINBOND::ChipErase() {
  WriteEnable();
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(CHIP_ERASE);
  digitalWrite(CS_PIN, HIGH);
  WriteDisable();
}

byte WINBOND::ManufactureID() {
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(R_MANUFAC_ID);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  SPI.transfer(0x00);
  byte manufacture_id = SPI.transfer(0xFF);
  digitalWrite(CS_PIN, HIGH);
  return manufacture_id;
}

byte WINBOND::Read_jedec_id() {
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(R_JEDEC_ID);
  byte jedec_id = SPI.transfer(0xFF);
  digitalWrite(CS_PIN, HIGH);
  return jedec_id;
}

void WINBOND::PowerDown() {
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(POWER_DOWN);
  digitalWrite(CS_PIN, HIGH);
}

void WINBOND::Write(long address, int data[], int data_size) {
  WriteEnable();
  delayMicroseconds(5);
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(WRITE);
  SPI.transfer((byte)((address >> 16) & 0x0000FF));
  SPI.transfer((byte)((address >> 8) & 0x0000FF));
  if (data_size == 256) {
    SPI.transfer(0x00);
  } else {
    SPI.transfer((byte)((address) & 0x0000FF));
  }

  for (int i = 0; i < data_size; i++) {
    SPI.transfer(data[i]);
  }
  digitalWrite(CS_PIN, HIGH);
  delayMicroseconds(100);
  WriteDisable();
}

void WINBOND::Read(bool FastRead) {
  unsigned long start_time = millis(); // Record the start time

  for (long i = 0x00000000; i <= 0xFF000000; i += 256) {
    digitalWrite(CS_PIN, LOW);
    if (FastRead) {
      SPI.transfer(FAST_READ);
    } else {
      SPI.transfer(READ);
    }
    SPI.transfer((byte)((i >> 16) & 0x000000FF));
    SPI.transfer((byte)((i >> 8) & 0x000000FF));
    SPI.transfer((byte)((i) & 0x000000FF));
    if (FastRead) {
      SPI.transfer(0x00);
    }
    for (int j = 0; j < 2048; j++) {
      byte data = SPI.transfer(0xFF);
      if (data < 0x10) {
        Serial.print("0");
      }
      Serial.print(data, HEX);
      // Print a space between each byte
      Serial.print(" ");
      // Print a newline character after every 16 bytes
      if ((j + 1) % 16 == 0) {
        Serial.println();
        unsigned long current_time = millis();
        unsigned long elapsed_time = current_time - start_time;
        unsigned long bytes_read_so_far = (i + j + 1) * 256; // Total bytes read so far
        unsigned long total_bytes = 0xFF000000; // Total bytes to read
        unsigned long bytes_remaining = total_bytes - bytes_read_so_far;
        unsigned long bytes_per_second = bytes_read_so_far / (elapsed_time / 1000); // Bytes per second
        unsigned long seconds_remaining = bytes_remaining / bytes_per_second; // Estimated seconds remaining
        unsigned long minutes_remaining = seconds_remaining / 60; // Convert seconds to minutes
        Serial.print("Time remaining: ");
        Serial.print(minutes_remaining);
        Serial.println(" minutes");
      }
    }

    digitalWrite(CS_PIN, HIGH);
    delayMicroseconds(250);
  }
}


void WINBOND::BlockErase(long address) {
  WriteEnable();
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(BLOCK_ERASE);
  SPI.transfer((byte)(address >> 16));
  SPI.transfer((byte)(address >> 8));
  SPI.transfer((byte) address);
  digitalWrite(CS_PIN, HIGH);
  delay(250);
  WriteDisable();
}

void WINBOND::SectorErase(long address) {
  WriteEnable();
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(SECTOR_ERASE);
  SPI.transfer((byte)(address >> 16));
  SPI.transfer((byte)(address >> 8));
  SPI.transfer((byte) address);
  digitalWrite(CS_PIN, HIGH);
  delay(1000);
  WriteDisable();
}