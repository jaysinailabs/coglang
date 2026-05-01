const FIXED_COMMIT_TIMESTAMP = "2026-04-18T00:00:00Z";

function ownerFromMessage(message) {
  return String(
    message?.metadata?.owner
    ?? message?.payload?.candidate?.owner
    ?? "unknown",
  );
}

function responseEnvelope(message, payloadKind, payload) {
  const header = message.header ?? {};
  return {
    header: {
      correlation_id: String(header.correlation_id ?? ""),
      message_type: "KnowledgeMessage",
      operation: "write_bundle_response",
      payload_kind: payloadKind,
      submission_id: String(header.submission_id ?? ""),
    },
    metadata: {
      ...(message.metadata ?? {}),
      owner: ownerFromMessage(message),
    },
    payload,
  };
}

function errorResponse(message, errors, errorKind = "ValidationError") {
  const header = message.header ?? {};
  return responseEnvelope(message, "ErrorReport", {
    correlation_id: String(header.correlation_id ?? ""),
    submission_id: String(header.submission_id ?? ""),
    owner: ownerFromMessage(message),
    error_kind: errorKind,
    retryable: false,
    errors,
  });
}

function validateSubmissionEnvelope(message) {
  const errors = [];
  if (message?.header?.message_type !== "KnowledgeMessage") {
    errors.push("header.message_type must be KnowledgeMessage");
  }
  if (message?.header?.operation !== "submit_write_bundle") {
    errors.push("header.operation must be submit_write_bundle");
  }
  if (typeof message?.header?.correlation_id !== "string") {
    errors.push("header.correlation_id must be a string");
  }
  if (typeof message?.header?.submission_id !== "string") {
    errors.push("header.submission_id must be a string");
  }
  const operations = message?.payload?.candidate?.operations;
  if (!Array.isArray(operations)) {
    errors.push("payload.candidate.operations must be an array");
  }
  return errors;
}

function phaseCounts() {
  return {
    phase_1a_create_nodes: 0,
    phase_1b_create_edges: 0,
    phase_1c_update_delete: 0,
  };
}

function applyOperation(graph, operation, index, counts, touchedNodeIds) {
  if (operation.op !== "create_node") {
    return [`op[${index}] unsupported op '${operation.op}'`];
  }
  const payload = operation.payload ?? {};
  if (typeof payload.id !== "string") {
    return [`op[${index}] create_node missing string id`];
  }
  if (typeof payload.node_type !== "string") {
    return [`op[${index}] create_node missing string node_type`];
  }
  if (graph.nodes.has(payload.id)) {
    return [`op[${index}] create_node duplicates id '${payload.id}'`];
  }
  graph.nodes.set(payload.id, {
    attrs: { ...(payload.attrs ?? {}) },
    node_type: payload.node_type,
  });
  counts.phase_1a_create_nodes += 1;
  touchedNodeIds.push(payload.id);
  return [];
}

export function createMinimalHost() {
  const graph = {
    nodes: new Map(),
  };
  const records = [];

  function submitMessage(message) {
    const envelopeErrors = validateSubmissionEnvelope(message);
    if (envelopeErrors.length > 0) {
      const response = errorResponse(message, envelopeErrors);
      records.push({ request: message, response, status: "failed" });
      return response;
    }

    const candidate = message.payload.candidate;
    const counts = phaseCounts();
    const touchedNodeIds = [];
    const trialGraph = {
      nodes: new Map(graph.nodes),
    };
    const errors = [];

    candidate.operations.forEach((operation, index) => {
      if (errors.length === 0) {
        errors.push(
          ...applyOperation(trialGraph, operation, index, counts, touchedNodeIds),
        );
      }
    });

    if (errors.length > 0) {
      const response = errorResponse(message, errors);
      records.push({ request: message, response, status: "failed" });
      return response;
    }

    graph.nodes = trialGraph.nodes;
    const response = responseEnvelope(message, "WriteResult", {
      applied_ops: candidate.operations.length,
      commit_timestamp: FIXED_COMMIT_TIMESTAMP,
      correlation_id: message.header.correlation_id,
      owner: ownerFromMessage(message),
      phase_counts: counts,
      submission_id: message.header.submission_id,
      touched_edge_refs: [],
      touched_node_ids: touchedNodeIds,
    });
    records.push({ request: message, response, status: "committed" });
    return response;
  }

  function localWriteHeader(correlationId) {
    const record = records.find(
      (item) => item.response.header.correlation_id === correlationId,
    );
    if (record === undefined) {
      return {
        correlation_id: correlationId,
        payload_kind: null,
        status: "not_found",
        submission_id: null,
      };
    }
    return {
      correlation_id: record.response.header.correlation_id,
      payload_kind: record.response.header.payload_kind,
      status: record.status,
      submission_id: record.response.header.submission_id,
    };
  }

  function exportState() {
    return {
      node_count: graph.nodes.size,
      nodes: [...graph.nodes.entries()].map(([id, payload]) => ({
        id,
        ...payload,
      })),
      record_count: records.length,
    };
  }

  return { exportState, localWriteHeader, submitMessage };
}
