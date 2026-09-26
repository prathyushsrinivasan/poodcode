// Declarations the editor's bundled TypeScript (5.4, inside monaco-editor
// 0.52) lacks but the judge's TypeScript (5.9, with the ES2024 + esnext libs
// listed in tscheck.rs) has. Without them the editor would underline code the
// judge accepts: `new Set(a).union(b)`, `gen().map(f).toArray()`,
// `Iterator.from(x)`, `Array.fromAsync(src)`, `Promise.try(f)`.
//
// Editor-only: the judge never sees this file. Keep the shapes close to the
// real lib signatures, and delete entries once Monaco's own TypeScript ships
// them — two declarations of the same method would become overloads.

export const MONACO_LIB_SHIMS = `
interface ReadonlySetLike<T> {
  keys(): Iterator<T>;
  has(value: T): boolean;
  readonly size: number;
}
interface Set<T> {
  union<U>(other: ReadonlySetLike<U>): Set<T | U>;
  intersection<U>(other: ReadonlySetLike<U>): Set<T & U>;
  difference<U>(other: ReadonlySetLike<U>): Set<T>;
  symmetricDifference<U>(other: ReadonlySetLike<U>): Set<T | U>;
  isSubsetOf(other: ReadonlySetLike<unknown>): boolean;
  isSupersetOf(other: ReadonlySetLike<unknown>): boolean;
  isDisjointFrom(other: ReadonlySetLike<unknown>): boolean;
}
interface ReadonlySet<T> {
  union<U>(other: ReadonlySetLike<U>): Set<T | U>;
  intersection<U>(other: ReadonlySetLike<U>): Set<T & U>;
  difference<U>(other: ReadonlySetLike<U>): Set<T>;
  symmetricDifference<U>(other: ReadonlySetLike<U>): Set<T | U>;
  isSubsetOf(other: ReadonlySetLike<unknown>): boolean;
  isSupersetOf(other: ReadonlySetLike<unknown>): boolean;
  isDisjointFrom(other: ReadonlySetLike<unknown>): boolean;
}
interface Iterator<T, TReturn = any, TNext = undefined> {
  map<U>(callbackfn: (value: T, index: number) => U): IterableIterator<U>;
  filter<S extends T>(predicate: (value: T, index: number) => value is S): IterableIterator<S>;
  filter(predicate: (value: T, index: number) => unknown): IterableIterator<T>;
  take(limit: number): IterableIterator<T>;
  drop(count: number): IterableIterator<T>;
  flatMap<U>(callback: (value: T, index: number) => Iterator<U> | Iterable<U>): IterableIterator<U>;
  reduce(callbackfn: (previousValue: T, currentValue: T, currentIndex: number) => T): T;
  reduce<U>(callbackfn: (previousValue: U, currentValue: T, currentIndex: number) => U, initialValue: U): U;
  toArray(): T[];
  forEach(callbackfn: (value: T, index: number) => void): void;
  some(predicate: (value: T, index: number) => unknown): boolean;
  every(predicate: (value: T, index: number) => unknown): boolean;
  find<S extends T>(predicate: (value: T, index: number) => value is S): S | undefined;
  find(predicate: (value: T, index: number) => unknown): T | undefined;
}
declare var Iterator: {
  from<T>(value: Iterator<T> | Iterable<T>): IterableIterator<T>;
};
interface ArrayConstructor {
  fromAsync<T>(iterableOrArrayLike: AsyncIterable<T> | Iterable<T | PromiseLike<T>> | ArrayLike<T | PromiseLike<T>>): Promise<T[]>;
  fromAsync<T, U>(iterableOrArrayLike: AsyncIterable<T> | Iterable<T> | ArrayLike<T>, mapFn: (value: Awaited<T>, index: number) => U, thisArg?: any): Promise<Awaited<U>[]>;
}
interface PromiseConstructor {
  try<T, U extends unknown[]>(callbackFn: (...args: U) => T | PromiseLike<T>, ...args: U): Promise<Awaited<T>>;
}
interface String {
  isWellFormed(): boolean;
  toWellFormed(): string;
}
`;
