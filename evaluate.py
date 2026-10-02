from evaluation_cases import evaluation_cases
from src.rag.pipeline import retrieve_documents


def evaluate_case(case: dict) -> tuple[bool, list[str]]:
    results = retrieve_documents(
        case["question"],
        user_id=case["user_id"],
        tenant_id=case["tenant_id"],
        user_roles=case["roles"],
    )

    retrieved_document_ids = {
        result.payload["document_id"]
        for result in results
    }

    allowed_documents_present = all(
        document_id in retrieved_document_ids
        for document_id in case["expected_allowed"]
    )

    forbidden_documents_retrieved = [
        document_id
        for document_id in case["expected_forbidden"]
        if document_id in retrieved_document_ids
    ]

    forbidden_documents_absent = (
        len(forbidden_documents_retrieved) == 0
    )

    passed = (
        allowed_documents_present
        and forbidden_documents_absent
    )

    return passed, forbidden_documents_retrieved


def run_evaluation() -> None:
    passed_cases = 0
    total_forbidden_leaks = 0

    for case in evaluation_cases:
        passed, forbidden_leaks = evaluate_case(case)

        status = "PASS" if passed else "FAIL"

        print(
            f"{status}: {case['name']}"
        )

        if forbidden_leaks:
            print(
                f"  Forbidden documents retrieved: "
                f"{forbidden_leaks}"
            )

        if passed:
            passed_cases += 1

        total_forbidden_leaks += len(
            forbidden_leaks
        )

    total_cases = len(evaluation_cases)
    accuracy = passed_cases / total_cases

    print()
    print(f"Cases passed: {passed_cases}/{total_cases}")
    print(f"Authorization accuracy: {accuracy:.2%}")
    print(
        f"Forbidden document leaks: "
        f"{total_forbidden_leaks}"
    )


if __name__ == "__main__":
    run_evaluation()