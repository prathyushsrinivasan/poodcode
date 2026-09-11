import { describe, it, expect } from "vitest";
import { pairExchanges, sampleRequests } from "./workbench";

describe("pairExchanges", () => {
  it("pairs each reply with the request that produced it", () => {
    const stdin = 'POST /todos {"title":"Buy milk"}\nGET /todos/1\nGET /todos/99\n';
    const stdout = '201 {"id":1,"title":"Buy milk","done":false}\n200 {"id":1}\n404 {"error":"not_found"}\n';
    expect(pairExchanges(stdin, stdout)).toEqual([
      { request: 'POST /todos {"title":"Buy milk"}', status: 201, body: '{"id":1,"title":"Buy milk","done":false}' },
      { request: "GET /todos/1", status: 200, body: '{"id":1}' },
      { request: "GET /todos/99", status: 404, body: '{"error":"not_found"}' },
    ]);
  });

  it("skips blank request lines exactly as the replayer does", () => {
    expect(pairExchanges("\nGET /todos\n\n", "200 []")).toEqual([
      { request: "GET /todos", status: 200, body: "[]" },
    ]);
  });

  it("reads a reply with an empty body — a 204", () => {
    expect(pairExchanges("DELETE /todos/1", "204")).toEqual([
      { request: "DELETE /todos/1", status: 204, body: "" },
    ]);
  });

  it("refuses to pair when the counts differ, rather than misalign", () => {
    expect(pairExchanges("GET /todos\nGET /todos", "200 []")).toBeNull();
  });

  it("refuses to pair when the handler printed lines of its own", () => {
    expect(pairExchanges("GET /todos", "handling GET /todos")).toBeNull();
    expect(pairExchanges("GET /a\nGET /b", "debug\n200 []")).toBeNull();
  });

  it("returns null for a program with no requests", () => {
    expect(pairExchanges("", "7")).toBeNull();
  });

  it("tolerates CRLF output", () => {
    expect(pairExchanges("GET /todos", "200 []\r\n")).toEqual([
      { request: "GET /todos", status: 200, body: "[]" },
    ]);
  });
});

describe("sampleRequests", () => {
  it("builds a request line per endpoint, filling path parameters", () => {
    const endpoints = [
      { method: "GET", path: "/todos", purpose: "", request: "", response: "", status: "200" },
      { method: "PATCH", path: "/todos/:id", purpose: "", request: '{"done":true}', response: "", status: "200" },
    ];
    expect(sampleRequests({ endpoints })).toEqual(["GET /todos", 'PATCH /todos/1 {"done":true}']);
  });
});
