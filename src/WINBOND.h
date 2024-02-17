#ifndef WINBOND_H
#define WINBOND_H

#include<Arduino.h>

#define WRITE_ENABLE  0x06
#define WRITE_DISABLE 0x04
#define R_STA_REG     0x05
#define W_STA_REG     0x01
#define WRITE         0x02
#define READ          0x03
#define FAST_READ     0x0B
#define FAST_READ_2   0x3B
#define BLOCK_ERASE   0xD8
#define SECTOR_ERASE  0x20
#define CHIP_ERASE    0xC7
#define POWER_DOWN    0xB9
#define R_POWER_DOWN  0xAB
#define HIGH_PF       0xA3
#define R_JEDEC_ID    0x9F
#define R_MANUFAC_ID  0x90
#define RESET         0xFF 

class WINBOND {
  private: int CS_PIN;
  public: void Init(int CS_PIN);
  void Reset();
  void Release_Power_Down();
  void WriteEnable();
  void WriteDisable();
  int chk_sta_reg();
  void ChipErase();
  byte ManufactureID();
  byte Read_jedec_id();
  void PowerDown();
  void Read(bool FastRead);
  void Write(long address, int data[], int data_size);
  void BlockErase(long address);
  void SectorErase(long address);
};

#endif