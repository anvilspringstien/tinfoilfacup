// Shared SQLite logic for Cloudflare and the local Shed. No Campaign data.
export class LikeStore {
 constructor(storage) {
  this.storage=storage;this.sql=storage.sql;
  this.sql.exec('CREATE TABLE IF NOT EXISTS reactions (token_hash TEXT PRIMARY KEY)');
  this.sql.exec('CREATE TABLE IF NOT EXISTS totals (id INTEGER PRIMARY KEY CHECK(id=1), total INTEGER NOT NULL CHECK(total>=0))');
  this.sql.exec('INSERT OR IGNORE INTO totals VALUES (1,0)');
 }
 state(hash) {return {liked:!!this.sql.exec('SELECT token_hash FROM reactions WHERE token_hash=?',hash).toArray().length};}
 set(hash,liked) {
  return this.storage.transactionSync(()=>{
   const prior=this.state(hash).liked;
   if(liked!==prior){
    if(liked)this.sql.exec('INSERT INTO reactions VALUES (?)',hash);
    else this.sql.exec('DELETE FROM reactions WHERE token_hash=?',hash);
    this.sql.exec('UPDATE totals SET total=total+? WHERE id=1',liked?1:-1);
   }
   return {liked};
  });
 }
 count(){return {total:Number(this.sql.exec('SELECT total FROM totals WHERE id=1').toArray()[0].total)};}
}
