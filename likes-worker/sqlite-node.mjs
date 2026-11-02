import {DatabaseSync} from 'node:sqlite';
export function openStorage(path=':memory:'){
 const db=new DatabaseSync(path);
 return {db,sql:{exec(query,...args){const rows=db.prepare(query).all(...args);return {toArray:()=>rows};}},transactionSync(fn){db.exec('BEGIN IMMEDIATE');try{const value=fn();db.exec('COMMIT');return value;}catch(error){db.exec('ROLLBACK');throw error;}}};
}
