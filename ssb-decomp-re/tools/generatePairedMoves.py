"""Compile bounded donor phases and independently sampled tether/capture paths."""
from pairedMoves import *
from generateCustomAnimations import vec as native_vec

def vec(values):
    # Round far below engine collision tolerance for reproducible host math.
    return native_vec(tuple(round(v,6)+0.0 for v in values))

def render():
    from sharedAnimation import catalog as animation_catalog,paired_rows
    cases,_=animation_catalog();out=['/* Generated paired grab/throw bindings. */'];bank=['/* Generated donor capture/collision geometry in the guarded fighter overlay. */'];seen={};records=[]
    for i,(c,indices) in enumerate(paired_rows()):
        symbol='sFTCustomPair'+str(i);key=(c['fighter'],c['name'],c['flags'],c['frames'])
        collisions,anchors,travel=phase_data(i)
        if key not in seen:
            seen[key]=symbol
            bank.append('const FTCustomPairAnchor '+symbol+'Anchors[] = {')
            bank.extend('    { { '+', '.join(vec(row) for row in r)+' }, '+vec(t)+' },' for r,t in anchors);bank.append('};')
            if any(any(v != 0 for v in t) for t in travel):
                bank.append('const Vec3f '+symbol+'Travel[] = { '+', '.join(vec(t) for t in travel)+' };')
        data=seen[key]
        has_travel=any(any(v != 0 for v in t) for t in travel)
        for type_,suffix in (('FTCustomPairAnchor','Anchors'),('Vec3f','Travel')):
            if suffix=='Travel' and not has_travel:continue
            out.append('extern const '+type_+' '+data+suffix+'[];')
        active=any(mask for mask,_ in collisions)
        if active:
            bank.append('const FTCustomCollisionFrame '+symbol+'Collisions[] = {')
            bank.extend('    { { '+', '.join(vec(t) for t in centers)+' }, '+str(mask)+' },' for mask,centers in collisions);bank.append('};')
            out.append('extern const FTCustomCollisionFrame '+symbol+'Collisions[];')
        out.append('const FTCustomAnimationClip *const '+symbol+'Clips[] = { '+', '.join('&'+cases[j]['symbol'] for j in indices)+' };')
        out.append('const ftMotionCommand '+symbol+'Script[] = { '+', '.join(c['script'])+' };')
        out.append('const ftMotionCommand '+symbol+'Visual[] = { '+', '.join(c['visual'])+' };')
        throws=throw_descriptors(c['fighter'],c['phase'])
        if throws:out.append('FTThrowHitDesc '+symbol+'Throws[] = { '+', '.join('{ '+', '.join(map(str,row))+' }' for row in throws)+' };')
        attachments=props(i)
        for p,(joint,part,frames) in enumerate(attachments):
            name=symbol+'Prop'+str(p)
            bank.append('const FTCustomSpecialAttachmentFrame '+name+'Frames[] = {')
            bank.extend('    { '+vec(r)+', '+vec(t)+', '+vec(sc)+', '+str(active)+' },' for r,t,sc,active in frames);bank.append('};')
            out.append('extern const FTCustomSpecialAttachmentFrame '+name+'Frames[];')
        if attachments:
            out.append('const FTCustomSpecialAttachment '+symbol+'Props[] = { '+', '.join('{ '+symbol+'Prop'+str(p)+'Frames, '+str(j)+', '+str(part)+', FALSE }' for p,(j,part,_) in enumerate(attachments))+' };')
        flags=2 if c['loop_period'] else 0
        records.append('    { '+str(c['donor'])+', '+str(c['status'])+', '+str(c['motion'])+', { '+symbol+'Script, ARRAY_COUNT('+symbol+'Script), '+str(c['duration'])+', '+str(flags)+' }, { '+(symbol+'Collisions' if active else 'NULL')+', 0, '+str(c['frames'])+', '+str(c['loop_start'])+', '+str(c['loop_period'])+' }, '+data+'Anchors, '+(data+'Travel' if has_travel else 'NULL')+', '+symbol+'Clips, '+str(c['frames'])+', '+symbol+'Visual, '+(symbol+'Throws' if throws else 'NULL')+', '+(symbol+'Props' if attachments else 'NULL')+', '+str(len(attachments))+' },')
    out.extend(('const FTCustomPairPhase sFTCustomPairPhases[] = {',*records,'};','const FTThrownStatus sFTCustomPairVictimStatuses[12][12][2] = {'))
    for row in victims():out.append('    { '+', '.join('{ { '+', '.join(row[i])+ ' }, { '+', '.join(row[i+1])+' } }' for i in range(0,24,2))+' },')
    out.append('};')
    return '\n'.join(out)+'\n','\n'.join(bank)+'\n'

def main():
    out,bank=render()
    (ROOT/'src/ft/ftpairedmoves.generated.inc').write_text(out,encoding='utf-8',newline='\n')
    (ROOT/'src/ft/ftpairedgeometry.generated.inc').write_text(bank,encoding='utf-8',newline='\n')
    print('Generated',len(catalog()),'paired phases and 288 victim status pairs.')
if __name__=='__main__':main()
