import IssueCard from "./IssueCard.jsx";
const COLUMNS=["Todo","In Progress","Done"];
function slug(value){return value.toLowerCase().replace(/\s+/g,"-")}
export default function KanbanBoard({issues,onChangeStatus,onDelete}){return <div className="kanban">{COLUMNS.map(column=>{const columnIssues=issues.filter(i=>i.status===column);return <div className="kanban-column" key={column} data-testid={`column-${slug(column)}`}><h3>{column} <span className="count">({columnIssues.length})</span></h3>{columnIssues.length===0?<p className="muted empty-column">No issues</p>:columnIssues.map(issue=><IssueCard key={issue.id} issue={issue} onChangeStatus={onChangeStatus} onDelete={onDelete}/>)}</div>})}</div>}
