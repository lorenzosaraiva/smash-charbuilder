#!/usr/bin/env python3
"""Verify host-tested tables and linked custom code are in the built US ROM."""
from pathlib import Path
import hashlib
import struct
from n64crc import calculate_crcs
from generateCustomMoves import MAPS, ROSTER
from verifyCustomMoveData import verify_sources
from elfData import read_elf
from customMoveTiming import animation_duration
from generateCustomCollisions import catalog, stored_frames
from generateNeutralProjectiles import catalog as projectile_catalog, render as render_projectiles
from generateNeutralActions import catalog as action_catalog, render as render_actions, yoshi_interrupt_throws
from generateSpecialTiming import catalog as special_catalog, render as render_specials, donkey_frames, path_catalog, GAMEPLAY_OPS, superjump_landing_duration, direct_landing_duration
from auditNormalMoves import enum_values
from generateNormalMechanics import catalog as normal_mechanics_catalog, render as render_normal_mechanics

ROOT = Path(__file__).resolve().parents[1]
rom = (ROOT/'build/smashbrothers.us.z64').read_bytes()
assert rom[:4] == b'\x80\x37\x12\x40'
assert calculate_crcs(rom) == struct.unpack_from('>II',rom,0x10)
host,sections,symbols = read_elf(ROOT/'build/testCustomMove','<')
verify_sources(host,sections,symbols)
metadata = {}
for name in ('sFTCustomMoves','sFTCustomGrabMoves'):
    address,length,index = symbols[name]
    start = sections[index][4]+address-sections[index][3]
    records = struct.unpack_from('<'+str(length//4)+'I',host,start)
    metadata[name] = [records[i+2:i+4] for i in range(0,len(records),4)]
checked = 0
excluded = ('sFTCustomMoves','sFTCustomMoveScripts','sFTCustomMotionIDs','sFTCustomJointMaps',
            'sFTCustomBodyExtraMotionIDs','sFTCustomLastAirAttack','sFTCustomGrabMoves',
            'sFTCustomGrabJointMap','sFTCustomGrabTimings','sFTCustomThrowDescs','sFTCustomMoveClocks')
for name,(address,length,index) in symbols.items():
    if not name.startswith('sFTCustom') or name.startswith(('sFTCustomAnimation','sFTCustomCollision')) or name in excluded: continue
    if not length or sections[index][1] == 8: continue
    start = sections[index][4]+address-sections[index][3]
    words = struct.unpack_from('<'+str(length//4)+'I',host,start)
    pattern = struct.pack('>'+str(length//4)+'I',*words)
    assert pattern in rom,'Missing collision data: '+name
    checked += 1
assert checked == 409,checked  # 396 normals, 12 grabs, one numeric throw table
joint_map = bytes(joint for fighter in ROSTER for joint in MAPS[fighter]+[0])
assert joint_map in rom
for name,format in (('sFTCustomGrabJointMap','B'),('sFTCustomGrabTimings','H')):
    address,length,index = symbols[name]
    start = sections[index][4]+address-sections[index][3]
    count = length//struct.calcsize(format)
    values = struct.unpack_from('<'+str(count)+format,host,start)
    assert struct.pack('>'+str(count)+format,*values) in rom,name
elf,sections,symbols = read_elf(ROOT/'build/smashbrothers.us.elf','>')
assert symbols['syTaskmanMalloc'][0]==0x80004980,'Main SDK/controller/ucode address layout moved'
assert symbols['osMemSize'][0]==0x80000318,'Incorrect IPL memory-size parameter'
for name in ('sSC1PTrainingModeStatusBuffer','sSCVSBattleStatusBuffer'):
    assert symbols[name][1] == 512*8, 'Full-roster donor asset cache: '+name
assert (ROOT/'src/ft/ftspecialtiming.generated.inc').read_text()==render_specials()
special_words=[v for donor,motion,duration,cycle,_ in special_catalog()
               for v in (donor,motion,0,0,duration,4 if cycle else 0)]
assert struct.pack('>'+str(len(special_words))+'I',*special_words) in rom,'Missing source special phase clocks'
dk_path=b''.join(struct.pack('>12fI',*(v for point in centers for v in point),mask)
                 for mask,centers in donkey_frames())
assert dk_path in rom,'Missing source DK hand-slap collision path'
print(f'PASS: {len(special_catalog())} source Up/Down B phase durations/loops and DK hit windows/geometry are linked in the ROM.')
for name,expected in metadata.items():
    address,length,index = symbols[name]
    start = sections[index][4]+address-sections[index][3]
    records = struct.unpack_from('>'+str(length//4)+'I',elf,start)
    assert [records[i+2:i+4] for i in range(0,len(records),4)] == expected, name+' donor duration/flags'
phoff = struct.unpack_from('>I',elf,28)[0]
size,count = struct.unpack_from('>HH',elf,42)
programs = [struct.unpack_from('>8I',elf,phoff+i*size) for i in range(count)]
opening_names=tuple('mvOpening'+name+'StartScene' for name in
                    ('Room','Portraits','Mario','Donkey','Samus','Fox','Link','Yoshi','Pikachu','Kirby',
                     'Run','Yoster','Cliff','Standoff','Yamabuki','Clash','Sector','Jungle','Newcomers'))
for name in ('ftMainSetStatus','ftMainPlayAnim','ftMainParseMotionEvent','ftMainProcPhysicsMap','ftMainHasCustomAttackTimeline',
             'ftMainUpdateComboStats','ftMainProcUpdateInterrupt',
             'ftMainCharBuilderTrySpecialN','ftMainCharBuilderIsImmediateDonkeyThrow',
             'ftMainCharBuilderGetSpecialTravel','ftMainCharBuilderGetSpecialSpawn',
             'ftMainCharBuilderGetSpecialWeapon','ftMainCharBuilderGetPikachuThunderDestroy',
             'ftMainCharBuilderGetSpecialSphere','ftMainCharBuilderAdjustSpecialCollision',
             'ftFoxSpecialAirHiSetStatusFromGround','ftFoxSpecialAirHiProcPhysics',
             'ftPikachuSpecialAirHiSetStatus','ftPikachuSpecialHiCheckGotoSubZip',
             'ftPikachuSpecialLwMakeThunder','ftPikachuSpecialLwCheckCollideThunder','ftPikachuSpecialLwProcDamage',
             'wpPikachuThunderHeadMakeWeapon','wpPikachuThunderHeadSetDestroy',
             'ftYoshiSpecialHiUpdateEggVars','ftYoshiSpecialHiGetEggPosition','ftYoshiSpecialHiProcDamage',
             'ftFoxSpecialLwStartInitStatusVars','ftNessSpecialLwInitVars','ftPurinSpecialHiProcUpdate',
             'ftCaptainSpecialHiProcCatch','ftCommonCaptureCaptainUpdatePositions','ftCaptainSpecialHiThrowSetStatus',
             'ftKirbySpecialLwCheckRelease','ftKirbySpecialLwSetDamageResist','ftKirbySpecialHiLandingProcUpdate',
             'gmCollisionCheckWeaponAttackSpecialCollide','gmCollisionCheckItemAttackSpecialCollide',
             'mnMapsStartScene',
             'ftMainCharBuilderSetSpecialTravelAngle',
             'ftMainCharBuilderGetSpecialTravelAngle','ftMainCharBuilderGetSuperJumpAttributes',
             'ftMarioSpecialHiProcInterrupt','ftMarioSpecialHiProcPhysics','ftMarioSpecialHiProcMap',
             'ftMarioSpecialHiProcUpdate','ftCommonFallSpecialSetStatus','ftCommonFallSpecialProcPhysics',
             'ftLinkSpecialHiUpdateWeaponAttack','ftLinkSpecialAirHiProcPhysics','ftLinkSpecialHiProcMap','ftLinkSpecialAirHiProcMap',
             'ftLinkSpecialHiMakeWeapon','ftLinkSpecialHiProcDamage','ftLinkSpecialHiDestroyWeapon',
             'ftLinkSpecialHiProcEffect','ftLinkSpecialHiEndProcUpdate','ftLinkSpecialAirHiProcUpdate',
             'wpLinkSpinAttackMakeWeapon','wpLinkSpinAttackProcUpdate','wpLinkSpinAttackProcMap',
             'ftSamusSpecialHiProcPhysics','ftSamusSpecialAirHiProcPhysics','ftSamusSpecialHiProcMap',
             'ftPhysicsApplyGroundVelFriction','ftPhysicsApplyAirVelFriction','ftPhysicsClampAirVelXMax',
             'ftMainCharBuilderGetSpecialAttributes','ftMainCharBuilderGetTornadoExpend',
             'ftPhysicsGetAirVelTransN','ftPhysicsApplyGroundVelTransN',
             'ftNessSpecialHiCheckCollidePKThunder','ftNessSpecialAirHiJibakuProcUpdate',
             'ftManagerSetupFilesPlayablesAll','wpMarioFireballMakeWeapon',
             'wpPikachuThunderJoltAirMakeWeapon','wpPikachuThunderJoltGroundMakeWeapon',
             'wpNessPKFireMakeWeapon','itNessPKFireMakeItem',
             'ftMainCharBuilderResetNeutralAll','ftMainCharBuilderResetNeutral',
             'ftMainCharBuilderBoomerangIsSmash','ftMainCharBuilderBoomerangClear',
             'ftMainCharBuilderBoomerangCatch','wpLinkBoomerangClearGObjs',
             'wpLinkBoomerangMakeWeapon','wpLinkBoomerangCheckOwnerCatch',
             'wpSamusChargeShotMakeWeapon','ftCommonCaptureYoshiProcCapture',
             'ftCommonCaptureYoshiProcCaptureWithPhysics',
             'ftCommonYoshiEggSetStatus','ftCommonThrownDecideFighterLoseGrip',
             'ftManagerAllocFighter','ftManagerInitFighter','syTaskmanUseExpansionArena',
             'mnPlayers1PTrainingStartScene','mnPlayersVSStartScene','scVSBattleStartScene',
             'ftCommonSpecialNCheckInterruptCommon','ftCommonSpecialAirCheckInterruptCommon',
             'ftCommonThrowSetStatus','ftDonkeyThrowFFProcUpdate','mnOptionBuilderChangeValue',
             'sc1PTrainingModeStartScene','mnPlayers1PTrainingBackTo1PMode',
             'mnPlayers1PTrainingInitVars','gSCManagerCharBuilderTrainingSlot',
             'mnOptionBuilderTestInTraining','mnOptionInitVars','mnOptionFuncStart',
             'ftCommonAttackAirLwProcHit','ftCommonAttackAirLwProcUpdate',
             'ftMainCharBuilderGetNormalKind','ftMainCharBuilderGetAttackAttributes',
             'ftMainCharBuilderGetJabStatus','ftMainCharBuilderHasNormalMotion',
             'ftMainCharBuilderGetNormalSphere','ftMainCharBuilderUsesNormalTransN',
             'ftCommonAttack11ProcUpdate','ftCommonAttack12ProcUpdate','ftCommonAttack13ProcUpdate',
             'ftCommonAttack100StartCheckInterruptCommon','ftCommonAttack100LoopProcUpdate',
             'ftCommonAttackS4SetStatus','ftCommonAttackS4ProcUpdate',
             'sc1PTrainingModeUpdateViewOption','mnOptionBuilderAssignPlayer','mnOptionBuilderRun',*opening_names,*metadata):
    value,length,index = symbols[name]
    assert length>0,name
    for typ,fileoffset,vaddr,paddr,filesz,memsz,flags,align in programs:
        if typ == 1 and vaddr <= value and value+length <= vaddr+filesz:
            delta = value-vaddr
            assert elf[fileoffset+delta:fileoffset+delta+length] == rom[paddr+delta:paddr+delta+length],name
            break
    else: raise AssertionError('Code missing from ROM: '+name)
assert 'gSCManagerCharBuilderPlayerSlots' in symbols
assert 'gFTCustomMoveValidationFailures' in symbols
assert 'gFTCustomAnimationValidationFailures' in symbols
expansion_call=struct.pack('>I',0x0C000000|((symbols['syTaskmanUseExpansionArena'][0]>>2)&0x03FFFFFF))
for name in opening_names:
    address,length,index=symbols[name]
    start=sections[index][4]+address-sections[index][3]
    assert expansion_call in elf[start:start+length],name+' missing Expansion Pak heap call'
print('PASS: all 19 intro scenes use the linked Expansion Pak heap helper.')
animation_bytes = 0
host,host_sections,host_symbols = read_elf(ROOT/'build/testCustomMove','<')
laser_addresses = []
for name in ('sFTCharBuilderLaserGround','sFTCharBuilderLaserAir','sFTCharBuilderNeutralStatuses'):
    address,length,index = host_symbols[name]
    start = host_sections[index][4]+address-host_sections[index][3]
    words = struct.unpack_from('<'+str(length//4)+'I',host,start)
    pattern = struct.pack('>'+str(length//4)+'I',*words)
    assert pattern in rom,name+' missing from ROM'
    if name != 'sFTCharBuilderNeutralStatuses':
        addresses = []
        for typ,fileoffset,vaddr,paddr,filesz,memsz,flags,align in programs:
            if typ != 1: continue
            offset = rom.find(pattern,paddr,paddr+filesz)
            while offset != -1:
                addresses.append(vaddr+offset-paddr)
                offset = rom.find(pattern,offset+1,paddr+filesz)
        assert addresses,name+' outside ROM load segments'
        laser_addresses.append(addresses)
address,length,index = host_symbols['sFTCharBuilderLaserMoves']
start = host_sections[index][4]+address-host_sections[index][3]
records = struct.unpack_from('<8I',host,start)
assert records[2] == animation_duration('&llFTFoxAnimLaserFileID') == 55
assert records[6] == animation_duration('&llFTFoxAnimLaserAerialFileID') == 45
# IDO omits local data names. Match the complete linked table with real script addresses.
assert any(struct.pack('>8I',ground,*records[1:4],air,*records[5:8]) in rom
           for ground in laser_addresses[0] for air in laser_addresses[1]),'Laser pointers/durations missing'
assert (ROOT/'src/ft/ftneutralprojectiles.generated.inc').read_text() == render_projectiles(), 'Stale projectile source data'
def host_words(name):
    address,length,index = host_symbols[name]
    start = host_sections[index][4]+address-host_sections[index][3]
    return struct.unpack_from('<'+str(length//4)+'I',host,start)
def loaded_words(address, count):
    for typ,offset,vaddr,paddr,filesz,memsz,flags,align in programs:
        if typ == 1 and vaddr <= address and address+count*4 <= vaddr+filesz:
            return struct.unpack_from('>'+str(count)+'I',rom,paddr+address-vaddr)
    return None
assert (ROOT/'src/ft/ftnormalmechanics.generated.inc').read_text()==render_normal_mechanics()
assert loaded_words(symbols['sFTCharBuilderYoshiInterruptThrows'][0],14) == tuple(v & 0xffffffff for row in yoshi_interrupt_throws() for v in row), 'Linked Egg Lay interrupted-release descriptors'
normal_records=loaded_words(symbols['sFTCustomNormalMechanics'][0],12*33*4)
assert normal_records is not None
for donor,row in enumerate(normal_mechanics_catalog()):
    for variant,c in enumerate(row):
        travel,socket,count,flags=normal_records[(donor*33+variant)*4:(donor*33+variant+1)*4]
        assert (count,flags)==(c['duration']+1,c['flags']),(donor,variant,'normal mechanics metadata')
        for pointer,points in ((travel,c['travel']),(socket,c['socket'])):
            if not points:assert pointer==0;continue
            words=loaded_words(pointer,len(points)*3);assert words is not None
            expected=struct.pack('>'+str(len(points)*3)+'f',*(v for p in points for v in p))
            assert struct.pack('>'+str(len(words))+'I',*words)==expected,(donor,variant,'normal source travel/socket')
print('PASS: 396 normal movement records, source root travel and Ness bat sockets match generated donor data in the ROM.')
for name in ('sFTCharBuilderProjectileOffsets','sFTCharBuilderProjectileDonors'):
    words=host_words(name)
    assert struct.pack('>'+str(len(words))+'I',*words) in rom, name
expected_scripts=[]
for case in projectile_catalog():
    words=host_words('sFTCharBuilderProjectile'+case['fighter']+str(case['air']))
    assert len(words)==3 and words[0]&0x3FFFFFF==case['firing']
    assert struct.pack('>3I',*words) in rom
    expected_scripts.append(words)
# Local symbol names may be stripped by IDO. Validate the full eight-definition
# table and every linked pointer in loadable RAM instead of searching raw words.
found=False
suffix=struct.pack('>3I',3,projectile_catalog()[0]['duration'],0)
for typ,offset,vaddr,paddr,filesz,memsz,flags,align in programs:
    if typ!=1: continue
    pos=rom.find(suffix,paddr+4,paddr+filesz)
    while pos!=-1:
        table=loaded_words(vaddr+pos-paddr-4,32)
        if table and all(tuple(table[i*4+1:i*4+4])==(3,case['duration'],0)
                         and loaded_words(table[i*4],3)==expected_scripts[i]
                         for i,case in enumerate(projectile_catalog())):
            found=True;break
        pos=rom.find(suffix,pos+1,paddr+filesz)
    if found:break
assert found,'Projectile pointers/timing table missing from ROM'
print('PASS: four selectable native projectiles, eight source timing/spawn definitions and resource preload code are linked in the ROM.')
assert (ROOT/'src/ft/ftneutralactions.generated.inc').read_text() == render_actions(), 'Stale neutral action source data'
action_records=host_words('sFTCharBuilderActions')
assert len(action_records)==30*12
ops=enum_values((ROOT/'src/ft/ftdef.h').read_text(),'FTMotionEvent')
for i,c in enumerate(action_catalog()):
    expected=[];tick=wall=0
    for op,args in c['events']:
        if op in ('ftMotionCommandWait','ftMotionCommandWaitAsync'):
            tick=int(args[0],0) if op.endswith('Async') else tick+int(args[0],0)
            wall=max(wall,tick);continue
        a=[int(v,0) for v in args] if 'AttackColl' in op or op.startswith('ftMotionCommandSetFlag') else []
        if op=='ftMotionCommandMakeAttackColl':
            aid,gid,jid,dmg,reb,element,size,x,y,z,angle,kbs,kbw,ga,sd,fl,fk,kbb=a
            words=(ops['nFTMotionEventMakeAttackColl']<<26|aid<<23|gid<<20|dmg<<5|reb<<4|element,
                   (size&65535)<<16|(x&65535),(y&65535)<<16|(z&65535),
                   (angle&1023)<<22|kbs<<12|kbw<<2|ga,(sd&255)<<24|fl<<21|fk<<17|kbb<<7)
        elif op=='ftMotionCommandClearAttackCollAll':words=(ops['nFTMotionEventClearAttackCollAll']<<26,)
        elif op.startswith('ftMotionCommandSetFlag'):words=(ops['nFTMotionEvent'+op[len('ftMotionCommand'):]]<<26|a[0],)
        else:continue
        expected.append((wall,words))
    words=host_words('sFTCharBuilderAction'+str(i)+'Script');actual=[];cursor=frame=0
    while cursor<len(words):
        word=words[cursor];opcode=word>>26;cursor+=1
        if opcode==ops['nFTMotionEventAsyncWait']:frame=word&0x3ffffff
        elif opcode==ops['nFTMotionEventEnd']:break
        elif opcode==ops['nFTMotionEventMakeAttackColl']:
            assert not word&(127<<13),'Foreign skeleton in neutral script'
            actual.append((frame,(word,*words[cursor:cursor+4])));cursor+=4
        else:actual.append((frame,(word,)))
    assert actual==expected,'Neutral source hit/flag/timing mismatch: '+str(i)
print('PASS: neutral damage, radii, offsets, angle, knockback, shield damage, hit groups and event timing match original packed source fields.')
action_payloads={}
for name,(address,length,index) in host_symbols.items():
    if name.startswith('sFTCharBuilderAction') and name!='sFTCharBuilderActions':
        words=host_words(name)
        assert struct.pack('>'+str(len(words))+'I',*words) in rom,name+' missing'
        action_payloads[address]=words
def action_table_matches(table):
    if table is None:return False
    for i,c in enumerate(action_catalog()):
        expected=action_records[i*12:(i+1)*12];actual=table[i*12:(i+1)*12]
        if actual[1:4]!=expected[1:4] or actual[5:9]!=expected[5:9]:return False
        if actual[2]!=c['duration']:return False
        for field in (0,4,9,10,11):
            pointer=expected[field]
            if not pointer:
                if actual[field]:return False
            elif loaded_words(actual[field],len(action_payloads[pointer]))!=action_payloads[pointer]:return False
    return True
found=False
suffix=struct.pack('>3I',*action_records[1:4])
for typ,offset,vaddr,paddr,filesz,memsz,flags,align in programs:
    if typ!=1:continue
    pos=rom.find(suffix,paddr+4,paddr+filesz)
    while pos!=-1:
        if action_table_matches(loaded_words(vaddr+pos-paddr-4,30*12)):
            found=True;break
        pos=rom.find(suffix,pos+1,paddr+filesz)
    if found:break
assert found,'Neutral action pointers/collision paths/sockets missing from ROM'
print('PASS: all 30 neutral phases and linked script, timing, collision, travel, projectile and capture pointers match host-tested data.')
# Verify the compiled special scripts against original packed source fields and
# follow every actual ROM pointer, including collision, travel and spawn arrays.
def verify_special_paths():
    host,sections,symbols=read_elf(ROOT/'build/testSpecialTiming','<')
    def words(name):
        address,length,index=symbols[name]
        start=sections[index][4]+address-sections[index][3]
        return struct.unpack_from('<'+str(length//4)+'I',host,start)
    payloads={}
    for name,(address,length,index) in symbols.items():
        if name.startswith('sFTCharBuilderSpecialPath') and name!='sFTCharBuilderSpecialPaths':
            data=words(name);payloads[address]=data
            pointer_script=name.endswith('Script') and bool(path_catalog()[int(name[len('sFTCharBuilderSpecialPath'):-len('Script')])]['throws'])
            if not pointer_script:
                assert struct.pack('>'+str(len(data))+'I',*data) in rom,name
    count=len(path_catalog())
    records=words('sFTCharBuilderSpecialPaths');assert len(records)==count*13
    for i,c in enumerate(path_catalog()):
        expected=[];wall=0
        for op,args in c['events']:
            if op=='ftMotionCommandWait':wall+=int(args[0],0);continue
            if op=='ftMotionCommandWaitAsync':wall=max(wall,int(args[0],0));continue
            if 'AttackColl' not in op and not op.startswith('ftMotionCommandSetFlag') and op not in GAMEPLAY_OPS:continue
            a=[int(v,0) for v in args]
            if op=='ftMotionCommandMakeAttackColl':
                aid,gid,jid,dmg,reb,element,size,x,y,z,angle,kbs,kbw,ga,sd,fl,fk,kbb=a
                data=(ops['nFTMotionEventMakeAttackColl']<<26|aid<<23|gid<<20|dmg<<5|reb<<4|element,
                      (size&65535)<<16|(x&65535),(y&65535)<<16|(z&65535),
                      (angle&1023)<<22|kbs<<12|kbw<<2|ga,(sd&255)<<24|fl<<21|fk<<17|kbb<<7)
            elif op in ('ftMotionCommandSetAttackCollSize','ftMotionCommandSetAttackCollDamage','ftMotionCommandSetAttackCollSoundLevel'):
                shift,bits={'ftMotionCommandSetAttackCollSize':(7,16),'ftMotionCommandSetAttackCollDamage':(15,8),'ftMotionCommandSetAttackCollSoundLevel':(20,3)}[op]
                data=(ops['nFTMotionEvent'+op[len('ftMotionCommand'):]]<<26|a[0]<<23|(a[1]&((1<<bits)-1))<<shift,)
            elif op=='ftMotionCommandSetAttackCollOffset':
                data=(ops['nFTMotionEventSetAttackCollOffset']<<26|a[0]<<23|(a[1]&65535)<<7,(a[2]&65535)<<16|(a[3]&65535))
            else:
                data=(ops['nFTMotionEvent'+op[len('ftMotionCommand'):]]<<26|(a[0] if a else 0),)
            expected.append((wall,data))
        data=words('sFTCharBuilderSpecialPath'+str(i)+'Script');actual=[];cursor=frame=0
        while cursor<len(data):
            word=data[cursor];opcode=word>>26;cursor+=1
            if opcode==ops['nFTMotionEventAsyncWait']:frame=word&0x3ffffff
            elif opcode==ops['nFTMotionEventEnd']:break
            elif opcode==ops['nFTMotionEventMakeAttackColl']:
                assert not word&(127<<13),'Foreign skeleton in special script'
                actual.append((frame,(word,*data[cursor:cursor+4])));cursor+=4
            elif opcode==ops['nFTMotionEventSetThrow']:
                assert data[cursor] in payloads,'Missing Falcon Dive throw data'
                cursor+=1
            elif opcode==ops['nFTMotionEventSetAttackCollOffset']:
                actual.append((frame,(word,data[cursor])));cursor+=1
            else:actual.append((frame,(word,)))
        assert actual==expected,('Special collision/flag source fields and event timing',c['phase'])
    def matches(table):
        if table is None:return False
        for i in range(count):
            expected=records[i*13:i*13+13];actual=table[i*13:i*13+13]
            if any(actual[f]!=expected[f] for f in (0,1,3,4,5,7,8,9,10)):return False
            for f in (2,6,11,12):
                pointer=expected[f]
                if not pointer:
                    if actual[f]:return False
                else:
                    native=loaded_words(actual[f],len(payloads[pointer]));host_data=payloads[pointer]
                    if native is None:return False
                    if f==2:
                        cursor=0
                        while cursor<len(host_data):
                            opcode=host_data[cursor]>>26
                            if native[cursor]!=host_data[cursor]:return False
                            if opcode==ops['nFTMotionEventSetThrow']:
                                throw=payloads[host_data[cursor+1]]
                                if loaded_words(native[cursor+1],len(throw))!=throw:return False
                                cursor+=2
                            else:
                                length=5 if opcode==ops['nFTMotionEventMakeAttackColl'] else 2 if opcode==ops['nFTMotionEventSetAttackCollOffset'] else 1
                                if native[cursor:cursor+length]!=host_data[cursor:cursor+length]:return False
                                cursor+=length
                    elif native!=host_data:return False
        return True
    prefix=struct.pack('>2I',*records[:2]);found=False
    for typ,offset,vaddr,paddr,filesz,memsz,flags,align in programs:
        if typ!=1:continue
        pos=rom.find(prefix,paddr,paddr+filesz)
        while pos!=-1:
            if matches(loaded_words(vaddr+pos-paddr,count*13)):found=True;break
            pos=rom.find(prefix,pos+1,paddr+filesz)
        if found:break
    assert found,'Special path registry/pointers missing from ROM'
    # IDO folds the address-selecting constants into anonymous rodata records.
    for duration in (superjump_landing_duration(),direct_landing_duration('Link'),direct_landing_duration('Samus')):
        assert struct.pack('>4I',0,0,duration,0) in rom,('Missing donor landing clock',duration)
    print(f'PASS: {count} source special scripts, damage/radii/knockback/flags/timing and linked collision/travel/spawn paths match checked data.')
verify_special_paths()
assert 'ftMainCharBuilderIsSpecialN' not in symbols  # Removed blanket laser interception.
for donor,frames in (('Captain',41),('Fox',28),('Donkey',61)):
    name = 'sFTCustomAnimation'+donor
    address,length,index = host_symbols[name]
    assert length == frames * 628
    start = host_sections[index][4]+address-host_sections[index][3]
    words = struct.unpack_from('<'+str(length//4)+'I',host,start)
    pattern = struct.pack('>'+str(length//4)+'I',*words)
    address,linked_length,index = symbols[name]
    start = sections[index][4]+address-sections[index][3]
    assert linked_length == length and elf[start:start+length] == pattern,name
    assert pattern in rom,name+' missing from ROM'
    animation_bytes += length
print('PASS: all three linked Mario animation pilots match host-tested poses and donor hitbox trajectories ('+str(animation_bytes)+' bytes).')
from sharedAnimation import catalog as animation_catalog
pose_cases,pose_rows=animation_catalog()
animation_names={name for name in host_symbols if name.startswith('sFTCustomAnimation')}
host_targets={host_symbols[name][0]:name for name in animation_names}
shared_bytes=0
for name in sorted(animation_names-{'sFTCustomAnimationCaptain','sFTCustomAnimationFox','sFTCustomAnimationDonkey'}):
    address,length,index=host_symbols[name]
    start=host_sections[index][4]+address-host_sections[index][3]
    raw=host[start:start+length]
    if name=='sFTCustomAnimationKeys':pattern=raw
    elif name=='sFTCustomAnimationCurves':
        pattern=b''.join(struct.pack('>IHH',*v) for v in struct.iter_unpack('<IHH',raw))
    elif name.endswith(('Curves','Root')):
        pattern=struct.pack('>'+str(length//2)+'H',*struct.unpack('<'+str(length//2)+'H',raw))
    elif name.startswith('sFTCustomAnimationSourceRig') and name.endswith('Bones'):
        pattern=b''.join(v[:4]+struct.pack('>4I',*struct.unpack('<4I',v[4:])) for v in (raw[i:i+20] for i in range(0,length,20)))
    elif name.startswith('sFTCustomAnimationSourceRig'):
        pointer,count=struct.unpack_from('<2I',raw)
        pattern=struct.pack('>2I',symbols[host_targets[pointer]][0],count)+raw[8:]
    elif name.startswith('sFTCustomAnimationRig') and name!='sFTCustomAnimationRigs':
        pattern=b''.join(v[:4]+struct.pack('>14I',*struct.unpack('<14I',v[4:])) for v in (raw[i:i+60] for i in range(0,length,60)))
    elif name=='sFTCustomAnimationRigs':
        pattern=b''.join(struct.pack('>2I',symbols[host_targets[pointer]][0],count) for pointer,count in struct.iter_unpack('<2I',raw))
    elif name=='sFTCustomAnimationClips':
        pointers=struct.unpack('<396I',raw)
        pattern=struct.pack('>396I',*(symbols[host_targets[p]][0] if p else 0 for p in pointers))
        for donor,row in enumerate(pose_rows):
            for variant,case_id in enumerate(row):
                expected=0 if case_id is None else host_symbols[pose_cases[case_id]['symbol']][0]
                assert pointers[donor*33+variant]==expected,('Animation registry',donor,variant)
    else:
        assert length==24,('Unexpected animation data',name,length)
        fields=list(struct.unpack('<6I',raw))
        fields[:3]=[symbols[host_targets[p]][0] for p in fields[:3]]
        pattern=struct.pack('>6I',*fields)
    linked_address,linked_length,index=symbols[name]
    start=sections[index][4]+linked_address-sections[index][3]
    assert linked_length==length and elf[start:start+length]==pattern,name+' linked data'
    for typ,offset,vaddr,paddr,filesz,memsz,flags,align in programs:
        if typ==1 and vaddr<=linked_address and linked_address+length<=vaddr+filesz:
            assert rom[paddr+linked_address-vaddr:paddr+linked_address-vaddr+length]==pattern,name+' ROM data'
            break
    else:raise AssertionError(name+' not loaded from ROM')
    shared_bytes+=length
print(f'PASS: {len(pose_cases)} shared normal clips, all 12 body rigs and 396 registry pointers match host-tested data ({shared_bytes} bytes).')
collision_bytes=0
cases,rows=catalog()
for case_id,case in enumerate(cases):
    first,frames=stored_frames(case_id)
    if not frames:continue
    name='sFTCustomCollision'+case['label']
    address,length,index=host_symbols[name]
    assert length==len(frames)*52
    start=host_sections[index][4]+address-host_sections[index][3]
    words=struct.unpack_from('<'+str(length//4)+'I',host,start)
    pattern=struct.pack('>'+str(length//4)+'I',*words)
    address,linked_length,index=symbols[name]
    start=sections[index][4]+address-sections[index][3]
    assert linked_length==length and elf[start:start+length]==pattern and pattern in rom,name
    collision_bytes+=length
name='sFTCustomCollisionTrajectories'
address,length,index=host_symbols[name]
assert length==12*33*20
start=host_sections[index][4]+address-host_sections[index][3]
host_records=struct.unpack_from('<'+str(length//4)+'I',host,start)
address,linked_length,index=symbols[name]
start=sections[index][4]+address-sections[index][3]
linked_records=struct.unpack_from('>'+str(length//4)+'I',elf,start)
assert linked_length==length
for i in range(0,len(host_records),5):
    assert host_records[i+1:i+5]==linked_records[i+1:i+5]
    if not host_records[i]:assert linked_records[i]==0;continue
    target=next(n for n,(v,_,_) in host_symbols.items() if n.startswith('sFTCustomCollision') and v==host_records[i])
    assert linked_records[i]==symbols[target][0],target
assert elf[start:start+length] in rom,'Trajectory registry missing from ROM'
print(f'PASS: full normal collision paths ({collision_bytes} bytes) and all 396 direct registry entries match host-tested data.')
print('PASS: 396 normal and 12 grab collision tables, all 36 two-part throw definitions, joint maps, grab timings, creator/assignment/training code and N64 CRC are in the ROM.')
print('PASS: selectable neutral dispatch, bounded laser scripts/durations and DK immediate throw dispatch are linked in the ROM.')
print('ROM bytes:',len(rom))
print('SHA-256:',hashlib.sha256(rom).hexdigest())
